# DATASET METADATA PROFILE: Gigaspeech2 Vietnamese (gigaspeech2_vie)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `doof-ferb/gigaspeech2_vie` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | SpeechColab (Mirror bởi doof-ferb) |
| **Giấy phép (License)** | Apache-2.0 / Non-commercial research |
| **Bài báo / Nguồn gốc** | [GigaSpeech 2 Paper](https://arxiv.org/abs/2406.11546) |
| **Dung lượng tải về (Download)** | `~3.51` GB |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~15 - 30` giờ (Ước lượng) | Cần kiểm tra lại chính xác số giờ của mirror này |
| **Tổng số mẫu (Samples)** | `11,035` mẫu | Tổng số dòng âm thanh trong repository |
| **Số giờ Train** | `...` giờ | |
| **Số giờ Validation** | `...` giờ | |
| **Số giờ Test** | `...` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Thu thập tự động từ nhiều kênh YouTube/Podcast |
| **Độ dài trung bình mỗi file** | `...` giây | |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav / Parquet | Native HF format |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Đã resample về 16 kHz |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Thu âm từ YouTube, Podcast, talkshow trực tuyến. Môi trường có thể chứa nhạc nền nhẹ, tiếng ồn môi trường hoặc tiếng vang phòng.
* **Miền ngữ cảnh (Domain):** Đa dạng: Tin tức, trò chuyện (Conversational), phỏng vấn, bài giảng, kể chuyện.
* **Phương ngữ (Dialects):** Đầy đủ giọng Bắc, Trung, Nam.

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `text` | Nhãn văn bản (transcription) | String |
| `speaker` | Mã định danh người nói | String |
| `id` | Mã định danh mẫu | String |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
ds = load_dataset("doof-ferb/gigaspeech2_vie", split="train")
print(ds[0])  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn tự động do hệ thống ASR chất lượng cao kết hợp với bộ lọc tinh lọc (Refined pseudo-labels). Baseline Zipformer-30M-RNNT-6000h đã dùng Whisper-large-v3-turbo để tinh chỉnh lại transcript bộ này.
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho GigaSpeech2 Vietnamese:**
1. **Tinh chỉnh nhãn bằng Whisper:** Do nhãn gốc là pseudo-label, cần chạy Whisper-large-v3-turbo inference trên toàn bộ audio rồi so khớp (align) với nhãn có sẵn. Giữ lại nhãn Whisper nếu confidence score > ngưỡng (vd: 0.85).
2. **Lọc nhiễu âm thanh:** Loại bỏ các mẫu chứa quá nhiều nhạc nền, tiếng vang, hoặc tín hiệu không phải tiếng nói (VAD filtering). Đặc biệt chú ý các đoạn intro/outro YouTube có nhạc.
3. **Lọc ký tự phi Việt:** Loại bỏ mẫu có tỉ lệ ký tự không thuộc bảng chữ cái tiếng Việt > 30% tổng transcript.
4. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.
5. **Xử lý từ lóng/viết tắt internet:** Transcript từ YouTube/Podcast thường chứa từ lóng (`ok`, `nha`, `đc`, `ko`) — cần chuẩn hóa theo từ điển viết tắt.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " '`)
- [ ] **Number → Text:** Chuyển số → chữ viết (bao gồm cả số điện thoại, ngày tháng, số tiền)
- [ ] **Special Characters:** Xóa ký tự đặc biệt, emoji, URL, hashtag, @mention
- [ ] **Foreign Words:** Chuẩn hóa từ tiếng Anh lẫn trong transcript theo từ điển chung
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt
- [ ] **Whisper Refinement:** Đã chạy Whisper-large-v3-turbo để tinh chỉnh lại nhãn

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> GigaSpeech2 vie thuộc nhóm **dữ liệu pseudo-labeled bổ sung** — đóng góp vào khối ~5,000 giờ pseudo-labeled trong baseline 6000h. Tuy mirror `doof-ferb` chỉ có ~11k mẫu, nên cần cân nhắc tải bản gốc `speechcolab/gigaspeech2` (6,000 giờ refined cho tiếng Việt) nếu muốn scale đúng baseline.
>
> **Ưu điểm:**
> Dữ liệu trích xuất từ môi trường nói thực tế (YouTube/Podcast) nên giọng điệu tự nhiên, từ vựng phong phú hiện đại. Rất quý giá để tăng tính generalization cho mô hình.
>
> **Nhược điểm & Rủi ro:**
> Nhãn là pseudo-label — dù đã tinh lọc vẫn có thể sai ở từ hiếm, tên riêng, thuật ngữ ngoại ngữ. Mirror `doof-ferb` chỉ chứa ~11k mẫu (rất ít so với bản gốc 6,000h). Âm thanh có thể lẫn nhạc nền, tiếng vang phòng.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Augmentation theo phân bố OOV:** Baseline Zipformer-30M áp dụng augmentation dựa trên phân bố token OOV (out-of-vocabulary) theo từng dataset. Với GigaSpeech2 (nội dung YouTube), tỉ lệ OOV sẽ cao hơn các dataset đọc sách → tăng weight augmentation (noise injection, pitch shift) cho các mẫu có OOV cao.
> - **Gợi ý scale data:** Nếu tài nguyên cho phép, nên tải bản `speechcolab/gigaspeech2` gốc (Vietnamese refined ~6,000h) thay vì chỉ dùng mirror ~11k mẫu.
> - **Thứ tự training:** Trong chiến lược train from scratch, nên đưa GigaSpeech2 vào **phase 2** (sau khi mô hình đã hội tụ sơ bộ trên dữ liệu sạch labeled) để tránh pseudo-label noise gây diverge sớm.

---
