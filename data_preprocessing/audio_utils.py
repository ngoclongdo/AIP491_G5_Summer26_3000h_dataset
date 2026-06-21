import os
import numpy as np
import librosa
import soundfile as sf
import torch
import torchaudio

def preprocess_audio(audio_input, target_sr=16000) -> tuple[np.ndarray, int]:
    """
    Load, resample, and convert audio to mono (16kHz).
    Handles both file paths and Hugging Face Dataset audio dicts:
    {"path": str, "array": ndarray, "sampling_rate": int}
    """
    # 1. Handle Hugging Face Audio Dictionary
    if isinstance(audio_input, dict) and "array" in audio_input:
        array = audio_input["array"]
        orig_sr = audio_input["sampling_rate"]
        
        # Convert to float32 numpy array
        if not isinstance(array, np.ndarray):
            array = np.array(array, dtype=np.float32)
        else:
            array = array.astype(np.float32)
            
        # Convert to mono if stereo
        if len(array.shape) > 1:
            array = np.mean(array, axis=1)
            
        # Resample if needed
        if orig_sr != target_sr:
            array = librosa.resample(array, orig_sr=orig_sr, target_sr=target_sr)
            
        return array, target_sr
        
    # 2. Handle File Path
    elif isinstance(audio_input, str):
        if not os.path.exists(audio_input):
            raise FileNotFoundError(f"Audio file not found: {audio_input}")
            
        # Load using torchaudio
        try:
            waveform, orig_sr = torchaudio.load(audio_input)
            
            # Convert to mono
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
                
            # Resample
            if orig_sr != target_sr:
                resampler = torchaudio.transforms.Resample(orig_sr, target_sr)
                waveform = resampler(waveform)
                
            array = waveform.squeeze(0).numpy()
            return array, target_sr
        except Exception as e:
            # Fallback to librosa
            array, _ = librosa.load(audio_input, sr=target_sr, mono=True)
            return array, target_sr
    else:
        raise ValueError("Invalid audio input. Must be a file path or Hugging Face audio dict.")

def get_duration(audio_array: np.ndarray, sr: int = 16000) -> float:
    """Return duration of audio in seconds."""
    return float(len(audio_array) / sr)

def is_valid_audio(audio_array: np.ndarray, sr: int = 16000, 
                   min_duration: float = 0.5, max_duration: float = 30.0) -> bool:
    """
    Validate audio: duration bounds, amplitude check (not silent/zero signal).
    """
    if audio_array is None or len(audio_array) == 0:
        return False
        
    # Check duration
    duration = get_duration(audio_array, sr)
    if duration < min_duration or duration > max_duration:
        return False
        
    # Check if the signal is not completely silent/zeros
    max_val = np.max(np.abs(audio_array))
    if max_val < 1e-4:  # threshold for dead channel or silent file
        return False
        
    return True

def save_wav(audio_array: np.ndarray, sr: int, output_path: str):
    """Save processed audio array as a WAV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, audio_array, sr, subtype='PCM_16')
