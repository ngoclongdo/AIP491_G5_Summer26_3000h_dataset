"""
Vietnamese ASR Dataset Preprocessing Pipeline
Tải dataset từ Hugging Face, chuẩn hóa text + audio, xuất Lhotse Manifests.

Sử dụng:
    python -m data_preprocessing.prepare_manifests --dataset fleurs --limit 10
    python -m data_preprocessing.prepare_manifests --streaming
    python -m data_preprocessing.prepare_manifests
"""

import os
import re
import logging
import argparse
import yaml
from tqdm import tqdm
from datasets import load_dataset
from lhotse import Recording, SupervisionSegment, RecordingSet, SupervisionSet

from data_preprocessing.audio_utils import preprocess_audio, is_valid_audio, save_wav, get_duration
from data_preprocessing.text_normalizer import normalize_text, is_valid_transcript

# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ============================================================
# CLI ARGUMENTS
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Preprocess Vietnamese ASR Datasets into Lhotse Manifests"
    )
    parser.add_argument("--config", type=str, default="configs/dataset_config.yaml",
                        help="Path to config YAML file")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Process only this specific dataset (e.g. fleurs)")
    parser.add_argument("--split", type=str, default=None,
                        help="Process only this specific split (e.g. train, test)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of samples processed (for quick testing)")
    parser.add_argument("--streaming", action="store_true",
                        help="Force HuggingFace dataset streaming mode for all datasets")
    return parser.parse_args()

# ============================================================
# DATASET PROCESSING
# ============================================================

# Datasets that are too large to fit in RAM — always use streaming
LARGE_DATASETS = {"viet_bud500", "VietSpeech", "viVoice"}

def process_dataset(ds_config, output_root, cache_dir,
                    force_streaming=False, target_split=None, limit=None):
    """
    Process a single dataset: download from HF → normalize text → resample audio
    → save WAVs → export Lhotse Manifests.
    """
    dataset_name = ds_config["name"]
    path = ds_config["path"]
    config_name = ds_config.get("config", "default")
    gated = ds_config.get("gated", False)
    splits = ds_config.get("splits", ["train"])
    mapping = ds_config["column_mapping"]

    use_streaming = force_streaming or (dataset_name in LARGE_DATASETS)

    logger.info("=" * 60)
    logger.info(f"Processing dataset: {dataset_name} ({path})")
    logger.info(f"Streaming mode: {use_streaming} | Gated: {gated}")
    logger.info("=" * 60)

    # Setup output directories
    ds_output_dir = os.path.join(output_root, dataset_name)
    os.makedirs(ds_output_dir, exist_ok=True)

    for split in splits:
        if target_split and split != target_split:
            continue

        logger.info(f"--- Processing split: {split} ---")
        wavs_dir = os.path.join(ds_output_dir, "wavs", split)
        os.makedirs(wavs_dir, exist_ok=True)

        # --------------------------------------------------
        # 1. Load dataset from Hugging Face
        # --------------------------------------------------
        try:
            dataset = load_dataset(
                path,
                name=config_name if config_name != "default" else None,
                split=split,
                cache_dir=cache_dir,
                streaming=use_streaming,
                token=True if gated else None,  # Modern HF datasets API
            )
        except Exception as e:
            logger.error(f"Failed to load {dataset_name} ({split}): {e}")
            logger.error("For gated datasets, authenticate first: huggingface-cli login")
            continue

        # --------------------------------------------------
        # 2. Iterate and process samples
        # --------------------------------------------------
        recordings = []
        supervisions = []

        # Progress bar total (unknown for streaming)
        total_samples = None
        if not use_streaming:
            total_samples = len(dataset)
            if limit:
                total_samples = min(total_samples, limit)

        pbar = tqdm(total=total_samples, desc=f"{dataset_name} [{split}]")
        count = 0
        skipped_text = 0
        skipped_audio = 0

        for item in dataset:
            if limit and count >= limit:
                break

            try:
                # --- Extract columns via config mapping ---
                audio_data = item[mapping["audio"]]
                raw_text = item[mapping["text"]]

                # --- Build unique sample ID with dataset prefix ---
                raw_id = None
                id_col = mapping.get("id")
                if id_col and id_col in item:
                    raw_id = str(item[id_col])

                if not raw_id:
                    raw_id = f"{split}_{count:07d}"

                # Always prefix with dataset name to avoid ID collisions when merging
                sample_id = f"{dataset_name}_{raw_id}"
                # Sanitize: only alphanumeric + underscores
                sample_id = re.sub(r'[^a-zA-Z0-9_]', '_', sample_id)

                # --- Text normalization ---
                normalized_text = normalize_text(raw_text)

                # Validate transcript (length + non-Vietnamese ratio filters)
                if not is_valid_transcript(normalized_text):
                    skipped_text += 1
                    continue

                # --- Audio preprocessing (resample → 16kHz mono) ---
                audio_array, sr = preprocess_audio(audio_data, target_sr=16000)

                # Validate audio (duration + amplitude)
                if not is_valid_audio(audio_array, sr):
                    skipped_audio += 1
                    continue

                # --- Save processed WAV ---
                wav_filename = f"{sample_id}.wav"
                wav_path = os.path.join(wavs_dir, wav_filename)
                save_wav(audio_array, sr, wav_path)

                # --- Create Lhotse manifest objects ---
                duration = get_duration(audio_array, sr)
                rel_wav_path = os.path.relpath(wav_path, start=output_root)

                recording = Recording.from_file(wav_path, recording_id=sample_id)
                recording.sources[0].source = rel_wav_path  # Use relative path for portability

                segment = SupervisionSegment(
                    id=sample_id,
                    recording_id=sample_id,
                    start=0.0,
                    duration=duration,
                    channel=0,
                    language="Vietnamese",
                    text=normalized_text
                )

                recordings.append(recording)
                supervisions.append(segment)
                count += 1

            except Exception as e:
                logger.warning(f"Error processing sample #{count} in {dataset_name}/{split}: {e}")

            finally:
                pbar.update(1)

        pbar.close()

        # --------------------------------------------------
        # 3. Save Lhotse Manifests
        # --------------------------------------------------
        if recordings:
            recording_set = RecordingSet.from_recordings(recordings)
            supervision_set = SupervisionSet.from_segments(supervisions)

            rec_path = os.path.join(ds_output_dir, f"{dataset_name}_recordings_{split}.jsonl.gz")
            sup_path = os.path.join(ds_output_dir, f"{dataset_name}_supervisions_{split}.jsonl.gz")

            recording_set.to_file(rec_path)
            supervision_set.to_file(sup_path)

            logger.info(f"Saved: {rec_path}")
            logger.info(f"Saved: {sup_path}")
        else:
            logger.warning(f"No valid samples for {dataset_name}/{split}.")

        logger.info(
            f"Summary [{dataset_name}/{split}]: "
            f"processed={count}, skipped_text={skipped_text}, skipped_audio={skipped_audio}"
        )

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    args = parse_args()

    # Read config
    if not os.path.exists(args.config):
        logger.error(f"Config file not found: {args.config}")
        return

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    output_root = config.get("output_dir", "data/processed")
    cache_dir = config.get("cache_dir", "data/raw_cache")

    for ds_config in config.get("datasets", []):
        if args.dataset and ds_config["name"] != args.dataset:
            continue

        process_dataset(
            ds_config=ds_config,
            output_root=output_root,
            cache_dir=cache_dir,
            force_streaming=args.streaming,
            target_split=args.split,
            limit=args.limit,
        )


if __name__ == "__main__":
    main()
