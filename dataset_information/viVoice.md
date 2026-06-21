# DATASET METADATA PROFILE: viVoice (viVoice)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `capleaf/viVoice` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | capleaf |
| **Giấy phép (License)** | CC-BY-NC-SA-4.0 (Chỉ dùng cho nghiên cứu phi thương mại) |
| **Bài báo / Nguồn gốc** | [capleaf/viVoice on Hugging Face](https://huggingface.co/datasets/capleaf/viVoice) |
| **Dung lượng tải về (Download)** | `~169` GB |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~1,017` giờ | Dành cho bài toán Speech Synthesis / TTS |
| **Tổng số mẫu (Samples)** | `887,772` mẫu | Tập dữ liệu multi-speaker chất lượng cao |
| **Số giờ Train** | `...` giờ | |
| **Số giờ Validation** | `...` giờ | |
| **Số giờ Test** | `...` giờ | |
| **Số lượng người nói (Speakers)** | `186` người | Tương ứng với 186 kênh YouTube |
| **Độ dài trung bình mỗi file** | `~4.1` giây | Đã trim bớt khoảng lặng vô ích ở đầu và cuối |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav | |
| **Tần số mẫu (Sample Rate)** | `24000` Hz | Lưu ý: Tần số mẫu cao phục vụ TTS. Đối với pipeline ASR cần downsample về 16kHz. |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit / 32-bit float | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Âm thanh phòng studio hoặc nơi thu âm yên tĩnh của các Youtuber. Đã được lọc nhiễu, loại bỏ âm nhạc và khoảng lặng dài thừa.
* **Miền ngữ cảnh (Domain):** Đọc truyện (Audiobooks), đọc tin tức, chia sẻ kiến thức, vlog (Multi-speaker studio-like quality).
* **Phương ngữ (Dialects):** Đa số là giọng đọc chuẩn (giọng Bắc hoặc giọng Nam).
* **Tỉ lệ giới tính:** Khoảng 61% giọng nam (Male).

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `text` | Nhãn văn bản (transcription) | String |
| `speaker_id`| Mã người nói (tương ứng với YouTube Channel ID) | String |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
# Gated dataset, cần đăng nhập HF trước qua CLI và được duyệt quyền truy cập
ds = load_dataset("capleaf/viVoice", split="train", streaming=True)
sample = next(iter(ds))
print(sample)  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn tự động kết hợp đối soát chỉnh sửa bán tự động chất lượng cao.
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho viVoice:**
1. **Resampling bắt buộc:** Audio gốc ở `24 kHz` — **BẮT BUỘC** downsample về `16 kHz` trước khi đưa vào pipeline ASR. Sử dụng `torchaudio.transforms.Resample(24000, 16000)` hoặc `librosa.resample`.
2. **Xử lý nội dung YouTube:** Transcript từ YouTuber có thể chứa: tên kênh, lời quảng cáo (`subscribe`, `like`, `đăng ký kênh`), URL kênh. Cần loại bỏ hoặc chuẩn hóa.
3. **Xử lý giọng đọc truyện:** Nhiều mẫu là audiobook/đọc truyện — transcript chứa dấu câu văn học (dấu ngoặc kép đối thoại, dấu gạch ngang `—`, dấu chấm lửng `…`).
4. **Speaker ID mapping:** Mỗi `speaker_id` tương ứng 1 kênh YouTube. Có thể dùng thông tin này để cân bằng tỉ lệ speaker trong batch training.
5. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.

**Checklist chuẩn hóa:**
- [ ] **Audio Resample:** Đã downsample từ 24kHz → 16kHz
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " ' — …`)
- [ ] **Number → Text:** Chuyển số → chữ viết
- [ ] **Special Characters:** Xóa ký tự đặc biệt, URL kênh YouTube, lời quảng cáo
- [ ] **Foreign Words:** Chuẩn hóa từ tiếng Anh lẫn trong transcript
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt

---

## VII. NHẬN XÉT(ENG LOGS)

> **Vai trò trong Pipeline:**
> viVoice thuộc nhóm **dữ liệu pseudo-labeled chất lượng cao** (~1,017 giờ). Trong baseline Zipformer-30M-RNNT-6000h, viVoice đóng góp đáng kể vào khối ~5,000 giờ pseudo-labeled. Tuy dataset ban đầu được thiết kế cho TTS, nhưng chất lượng audio studio-like cực tốt cho ASR. Thuộc nhóm **phase 2 training**.
>
> **Ưu điểm:**
> Chất lượng audio phòng thu cực tốt, không lẫn nhạc hay tạp âm. Giọng đọc rõ ràng, mạch lạc. Đa dạng 186 speakers. Tổng ~1,017 giờ — đóng góp lớn vào pool training.
>
> **Nhược điểm & Rủi ro:**
> Dung lượng cực lớn (~169GB). Gated dataset — yêu cầu email học thuật/tổ chức, có thể bị từ chối. **Sample rate 24kHz** khác chuẩn pipeline ASR (16kHz) — bắt buộc thêm bước resample. Giấy phép **CC-BY-NC-SA-4.0** cấm thương mại trực tiếp. Giọng đọc thiên studio — ít đại diện cho hội thoại tự nhiên.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 2 — Pseudo-labeled expansion:** Sau khi mô hình đã hội tụ sơ bộ trên phase 1 (dữ liệu labeled sạch), đưa viVoice vào cùng GigaSpeech2 để mở rộng pool training.
> - **Resampling pipeline:** Thêm `torchaudio.transforms.Resample(24000, 16000)` vào data pipeline. Kiểm tra kỹ chất lượng audio sau resample — 24→16kHz thường không gây loss chất lượng đáng kể cho ASR.
> - **Speaker balancing:** Tận dụng `speaker_id` để đảm bảo mỗi epoch không bị dominate bởi 1-2 speaker có quá nhiều mẫu.
> - **Augmentation nhẹ:** Vì audio gốc rất sạch, chỉ cần augmentation nhẹ (noise injection mức thấp, low-bitrate simulation) để tăng robustness.

---
