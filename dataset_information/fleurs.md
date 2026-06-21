# DATASET METADATA PROFILE: google/fleurs (vi_vn)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `google/fleurs` |
| **Subset / Config** | `vi_vn` |
| **Tác giả / Tổ chức** | Google |
| **Giấy phép (License)** | CC-BY-4.0 |
| **Bài báo / Nguồn gốc** | [FLEURS Paper](https://arxiv.org/abs/2205.12446) |
| **Dung lượng tải về (Download)** | `~1.5` GB (riêng subset `vi_vn`) |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~12` giờ | Tính trên toàn bộ tập dữ liệu vi_vn |
| **Tổng số mẫu (Samples)** | `4,416` mẫu | Tổng số dòng dữ liệu |
| **Số giờ Train** | `~8.3` giờ | 3,040 mẫu |
| **Số giờ Validation** | `~1.1` giờ | 418 mẫu |
| **Số giờ Test** | `~2.6` giờ | 958 mẫu |
| **Số lượng người nói (Speakers)** | `~200+` người | Có phân chia theo giới tính (gender) |
| **Độ dài trung bình mỗi file** | `~10` giây | Độ dài khá đồng đều |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Đã đúng chuẩn 16 kHz |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Thu âm qua smartphone/laptop trong nhà, môi trường tương đối ít nhiễu (Crowdsourced read speech)
* **Miền ngữ cảnh (Domain):** Giọng đọc sách/tin tức (Read Speech từ Wikipedia sentences)
* **Phương ngữ (Dialects):** Đầy đủ 3 miền Bắc - Trung - Nam

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `id` | Mã định danh mẫu | Int |
| `num_samples` | Số lượng mẫu âm thanh | Int |
| `path` | Đường dẫn file âm thanh | String |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `transcription` | Nhãn văn bản (đã viết thường/xóa dấu câu nhẹ) | String |
| `raw_transcription`| Nhãn văn bản gốc (còn dấu câu, viết hoa) | String |
| `gender` | Giới tính người nói | ClassLabel (Male/Female) |
| `lang_id` | Mã định danh ngôn ngữ | ClassLabel |
| `language` | Tên ngôn ngữ | String |
| `lang_group_id` | Nhóm ngôn ngữ | ClassLabel |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
ds = load_dataset("google/fleurs", "vi_vn", split="train")
print(ds[0])  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn do người đọc trực tiếp từ văn bản Wikipedia (Human-labeled). Dataset cung cấp cả `raw_transcription` (còn dấu câu, viết hoa) và `transcription` (đã chuẩn hóa sơ bộ).
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho FLEURS vi_vn:**
1. **Chọn cột transcript:** Sử dụng cột `raw_transcription` làm nguồn gốc, sau đó áp dụng pipeline chuẩn hóa thống nhất (không dùng `transcription` đã xử lý sẵn để đảm bảo nhất quán với các dataset khác).
2. **Xử lý tên riêng ngoại ngữ:** Transcript Wikipedia chứa nhiều tên riêng nước ngoài (tên quốc gia, tên nhân vật lịch sử). Cần giữ nguyên dạng viết hoặc Việt hóa nhất quán theo từ điển chuẩn hóa chung.
3. **Xử lý dấu ngoặc/tham chiếu:** Loại bỏ các ký hiệu dạng `[1]`, `(xem thêm)`, dấu ngoặc kép kép lồng nhau do nguồn gốc Wikipedia.
4. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ các mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " ' ( ) [ ]`)
- [ ] **Number → Text:** Chuyển số → chữ viết (`2026` → `hai nghìn không trăm hai mươi sáu`)
- [ ] **Special Characters:** Xóa ký tự đặc biệt, emoji, URL, ký hiệu Wikipedia
- [ ] **Foreign Words:** Chuẩn hóa tên riêng ngoại ngữ theo từ điển chung
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa, tab, newline → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> FLEURS vi_vn **KHÔNG** dùng để training — chỉ dùng làm **tập benchmark evaluation** chính. Đây là cách tiếp cận giống hệt baseline Zipformer-30M-RNNT-6000h, nơi FLEURS test set được dùng để báo cáo WER%.
>
> **Ưu điểm:**
> Transcript chất lượng cao do con người gõ, âm thanh sạch, đa dạng người nói. Tập test có 958 mẫu — đủ lớn để WER có ý nghĩa thống kê. Là chuẩn benchmark được cộng đồng ASR tiếng Việt công nhận rộng rãi.
>
> **Nhược điểm & Rủi ro:**
> Chỉ có ~12 giờ tổng cộng — quá ít để training. Giọng đọc Wikipedia (read speech) không đại diện cho hội thoại tự nhiên, nên WER trên FLEURS không phản ánh hoàn toàn hiệu năng thực tế.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> Vì kiến trúc Zipformer đã được cải tiến nên không thể load checkpoint từ baseline Zipformer-30M-RNNT-6000h. Cách tiếp cận:
> - Dùng FLEURS test set làm **evaluation benchmark xuyên suốt quá trình training** để so sánh trực tiếp WER với con số baseline đã công bố.
> - Tập train (~3,040 mẫu) có thể dùng bổ sung vào pool training chung nhưng đóng góp rất nhỏ (~8h).
> - **Quan trọng:** Đảm bảo pipeline chuẩn hóa text cho evaluation trên FLEURS phải **giống hệt** pipeline chuẩn hóa khi training để WER có ý nghĩa so sánh.

---
