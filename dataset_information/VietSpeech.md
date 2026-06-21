# DATASET METADATA PROFILE: VietSpeech (VietSpeech)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `NhutP/VietSpeech` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | Multimedia Communications Laboratory (MMLab-UIT) |
| **Giấy phép (License)** | Apache-2.0 |
| **Bài báo / Nguồn gốc** | [MMLab-UIT ASR Research](https://huggingface.co/datasets/NhutP/VietSpeech) |
| **Dung lượng tải về (Download)** | `~131` GB |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `> 1,100` giờ | |
| **Tổng số mẫu (Samples)** | `~1,030,000` mẫu | Quy mô cực kỳ lớn |
| **Số giờ Train** | `...` giờ | |
| **Số giờ Validation** | `...` giờ | |
| **Số giờ Test** | `...` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Thu thập từ đa dạng nguồn lực cộng đồng |
| **Độ dài trung bình mỗi file** | `~3.8` giây | Ước lượng dựa trên tổng số giờ và số mẫu |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Đã resample chuẩn |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Đa dạng: Crowdsourced qua smartphone, mạng xã hội, voice clips từ môi trường thực tế đời sống. Có thể chứa nhiều loại tạp âm nền khác nhau.
* **Miền ngữ cảnh (Domain):** Đọc truyện/sách (Read Speech), hội thoại tự do, thảo luận trên mạng xã hội.
* **Phương ngữ (Dialects):** Đầy đủ 3 miền Bắc, Trung, Nam với nhiều chất giọng địa phương phong phú.

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `text` | Nhãn văn bản (transcription) | String |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
# Khuyến nghị dùng streaming do dung lượng dataset lớn
ds = load_dataset("NhutP/VietSpeech", split="train", streaming=True)
sample = next(iter(ds))
print(sample)  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn do con người gõ và kiểm duyệt (Human-labeled/Verified)
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho VietSpeech:**
1. **Lọc chất lượng audio crowdsourced:** Dữ liệu thu thập từ đa nguồn cộng đồng nên chất lượng không đồng đều. Cần lọc SNR thấp, bỏ các file chứa quá nhiều tiếng ồn nền (giao thông, quán cà phê, tiếng gió).
2. **Xử lý nội dung mạng xã hội:** Transcript có thể chứa nội dung từ mạng xã hội — cần xử lý emoji text (`:)`, `^^`), viết tắt (`dk`, `cx`, `trc`, `dc`), từ lóng.
3. **Xử lý đa dạng phương ngữ:** VietSpeech bao phủ rộng 3 miền với nhiều chất giọng địa phương. Cần đảm bảo pipeline chuẩn hóa text không vô tình loại bỏ các từ phương ngữ hợp lệ (vd: `mần` = `làm`, `bửa` = `bữa`).
4. **Lọc theo độ dài:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự. Loại bỏ audio < 1 giây hoặc > 30 giây.
5. **Lọc tỉ lệ ký tự phi Việt:** Loại bỏ mẫu có tỉ lệ ký tự đặc biệt/phi Việt > 30%.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " '`)
- [ ] **Number → Text:** Chuyển số → chữ viết (bao gồm cả số điện thoại, ngày tháng)
- [ ] **Special Characters:** Xóa ký tự đặc biệt, emoji text, URL
- [ ] **Foreign Words:** Chuẩn hóa từ tiếng Anh lẫn trong transcript theo từ điển chung
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt
- [ ] **Dialect Preservation:** Đã kiểm tra không loại bỏ nhầm từ phương ngữ hợp lệ

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> VietSpeech là **dataset labeled lớn nhất** (>1,100 giờ) — chiếm phần lớn nhất trong khối ~1,000 giờ labeled của baseline 6000h. Đây là **xương sống của phase 1 training** (core training với nhãn sạch). Trong bối cảnh train from scratch, VietSpeech đóng vai trò **quan trọng nhất** vì không thể load checkpoint baseline.
>
> **Ưu điểm:**
> Quy mô cực lớn (>1,100 giờ, ~1 triệu mẫu), đa dạng accents và môi trường ghi âm thực tế. Nhãn do con người kiểm duyệt — chất lượng đáng tin cậy. Là nguồn dữ liệu chính để mô hình học acoustic model cơ bản. Được phát triển bởi MMLab-UIT — nhóm nghiên cứu ASR tiếng Việt uy tín.
>
> **Nhược điểm & Rủi ro:**
> Dung lượng tải về cực lớn (~131GB). Gated dataset — cần đồng ý điều khoản. Chất lượng audio không đồng đều do crowdsourced. Một số file có thể quá ngắn hoặc quá dài, cần lọc kỹ.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 1 — Core dataset chính:** VietSpeech nên là dataset đầu tiên và lớn nhất trong giai đoạn core training. Kết hợp với VietBud500, VLSP2020, FPT FOSD để tạo nền tảng acoustic model vững chắc.
> - **Curriculum learning:** Do quy mô rất lớn, có thể áp dụng curriculum learning: bắt đầu với các mẫu sạch nhất (SNR cao, transcript ngắn) rồi dần mở rộng sang các mẫu khó hơn.
> - **Augmentation theo phân bố OOV:** Baseline Zipformer-30M đặc biệt tăng augmentation cho các mẫu chứa nhiều OOV token. Với VietSpeech (nội dung đời sống), OOV chủ yếu là tên riêng và từ mượn — cần noise injection + speech permutation cho nhóm này.
> - **Data loading:** Bắt buộc dùng `lhotse` + `webdataset` hoặc lazy loading. Không load toàn bộ vào RAM.

---