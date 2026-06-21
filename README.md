# Vietnamese ASR Dataset Preprocessing Pipeline

Pipeline tải, tiền xử lý và chuẩn hóa các bộ dữ liệu Speech-to-Text tiếng Việt thành định dạng chuẩn **Lhotse Manifests**, sẵn sàng tích hợp vào các framework huấn luyện như `icefall` / `k2` (đặc biệt tối ưu cho kiến trúc **Zipformer-30M-RNNT**).

---

## 📂 Cấu trúc dự án

```text
speech_to_text/
├── configs/
│   └── dataset_config.yaml     # Cấu hình Hugging Face Repo, splits, và mapping cột
├── data_preprocessing/
│   ├── __init__.py
│   ├── audio_utils.py          # Xử lý âm thanh (resampling 16kHz, mono, VAD, check im lặng)
│   ├── text_normalizer.py      # Bộ chuẩn hóa text tiếng Việt (Unicode NFC, số->chữ, viết tắt...)
│   └── prepare_manifests.py    # Driver script tải từ Hugging Face → chuẩn hóa → xuất Lhotse manifests
├── dataset_information/        # Metadata chi tiết của từng bộ dữ liệu & báo cáo tổng hợp
│   ├── dataset_synthesis.md    # Báo cáo tổng hợp quy mô và phân pha training
│   └── ...
├── requirements.txt            # Thư viện phụ thuộc
└── README.md                   # Hướng dẫn sử dụng
```

---

## ✨ Các tính năng nổi bật

### 1. Tiền xử lý âm thanh (Audio Processing)
*   **Resampling chuẩn hóa:** Tự động downsample toàn bộ âm thanh về **16 kHz Mono** (ví dụ bộ `viVoice` gốc 24kHz sẽ được tự động hạ mẫu).
*   **Lọc nhiễu & thời lượng:** Loại bỏ các tệp tin âm thanh quá ngắn (<0.5 giây), quá dài (>30 giây) hoặc bị lỗi kênh câm (amplitude cực đại < 1e-4).

### 2. Chuẩn hóa văn bản tiếng Việt (Vietnamese Text Normalization)
*   **Unicode NFC:** Chuẩn hóa dấu tiếng Việt về dạng NFC thống nhất để so khớp ký tự chính xác.
*   **Đọc số tiếng Việt:** Tự động dịch số nguyên và số thập phân sang chữ quốc ngữ (ví dụ: `2026` → `hai nghìn không trăm hai mươi sáu`, `3.5` → `ba phẩy năm`).
*   **Mở rộng đơn vị đo:** Tách và dịch các đơn vị đo phổ biến đứng cạnh chữ số (ví dụ: `500mg` → `năm trăm mi li gam`, `170cm` → `một trăm bảy mươi xen ti mét`).
*   **Dịch từ viết tắt:** Tự động mở rộng từ viết tắt hội thoại/mạng xã hội (ví dụ: `ko` → `không`, `dc` → `được`, `cx` → `cũng`).
*   **Xóa ký tự rác:** Loại bỏ URL, email, hashtag, emoji chat (`:)`, `^^`), các tag ghi chú lỗi của ASR (`<unk>`, `<noise>`) và ký hiệu Wikipedia (`[1]`).

### 3. Bộ lọc chất lượng dữ liệu (Quality Filtering)
*   **Bộ lọc độ dài:** Bỏ các mẫu có transcript sau chuẩn hóa ngắn hơn 10 ký tự hoặc dài hơn 1000 ký tự.
*   **Lọc ký tự phi Việt:** Loại bỏ mẫu chứa hơn 30% ký tự đặc biệt/ngoại ngữ không thuộc bảng chữ cái tiếng Việt.

### 4. Định dạng Lhotse Manifests
*   Xuất dữ liệu ra các cặp file manifest nén `.jsonl.gz` gồm: `{dataset}_recordings_{split}.jsonl.gz` và `{dataset}_supervisions_{split}.jsonl.gz`.
*   Sử dụng đường dẫn tương đối (relative path) giúp di chuyển thư mục dữ liệu sang các server GPU khác mà không bị lỗi path âm thanh.

---

## 📊 Tổng quan 8 bộ dữ liệu hỗ trợ

| Tên Dataset | Hugging Face Repo | Tổng số giờ | Dạng Nhãn (Label Type) | Lộ trình huấn luyện |
| :--- | :--- | :--- | :--- | :--- |
| **VietSpeech** | `NhutP/VietSpeech` | `~1,100` giờ | Labeled (Human) | **Phase 1** (Core AM) |
| **viVoice** | `doof-ferb/viVoice` | `~1,017` giờ | Pseudo-labeled | **Phase 2** (Expansion) |
| **VietBud500** | `linhtran92/viet_bud500` | `~500` giờ | Labeled (Verified) | **Phase 1** (Core AM) |
| **FPT FOSD** | `doof-ferb/fpt_fosd` | `~100` giờ | Labeled (Human) | **Phase 1** (Core AM) |
| **VLSP 2020** | `doof-ferb/vlsp2020_vinai_100h` | `~100` giờ | Labeled (Human) | **Phase 1** (Core AM) |
| **VietMed Labeled**| `doof-ferb/VietMed_labeled` | `~16` giờ | Labeled (Medical) | **Phase 3** (Domain Adaptation) |
| **FLEURS vi_vn** | `google/fleurs` (vi_vn) | `~12` giờ | Labeled (Human) | **Evaluation** (WER Benchmark) |
| **GigaSpeech 2** | `doof-ferb/gigaspeech2_vie` | `~11` giờ | Pseudo-labeled | **Phase 2** (Expansion) |

---

## 🚀 Hướng dẫn cài đặt & sử dụng

### 1. Cài đặt môi trường
Yêu cầu Python >= 3.8 và đã cài đặt PyTorch. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 2. Đăng nhập Hugging Face (Bắt buộc cho các dataset gated)
Đối với các bộ dữ liệu gated như `viet_bud500`, `VietSpeech`, `viVoice`, bạn cần đăng nhập tài khoản Hugging Face đã được cấp quyền:
```bash
huggingface-cli login
```

### 3. Chạy tiền xử lý dữ liệu

Chương trình hỗ trợ chế độ **Streaming (lazy loading)** cho các bộ dữ liệu lớn (>100GB) để tiết kiệm ổ cứng và RAM.

*   **Chạy thử nghiệm (Giới hạn 10 mẫu để test nhanh):**
    ```bash
    python -m data_preprocessing.prepare_manifests --dataset fleurs --limit 10
    ```
*   **Chạy xử lý toàn bộ một dataset:**
    ```bash
    python -m data_preprocessing.prepare_manifests --dataset fleurs
    ```
*   **Chạy xử lý toàn bộ cả 8 bộ dữ liệu:**
    ```bash
    python -m data_preprocessing.prepare_manifests
    ```
*   **Ép buộc chế độ streaming cho toàn bộ các dataset:**
    ```bash
    python -m data_preprocessing.prepare_manifests --streaming
    ```

Dữ liệu đầu ra (file âm thanh WAV đã chuẩn hóa và tệp manifest) sẽ được lưu tại thư mục `data/processed/<tên_dataset>/`.
