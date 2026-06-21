# DATASET METADATA PROFILE: FPT Open Speech Dataset (fpt_fosd)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `doof-ferb/fpt_fosd` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | FPT Corporation (Mirror bởi doof-ferb) |
| **Giấy phép (License)** | CC-BY-4.0 |
| **Bài báo / Nguồn gốc** | [FPT Open Speech Dataset (2018)](https://huggingface.co/datasets/doof-ferb/fpt_fosd) |
| **Dung lượng tải về (Download)** | `~10 - 15` GB (Ước lượng) |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~100` giờ | Tính trên toàn bộ tập dữ liệu |
| **Tổng số mẫu (Samples)** | `25,900` mẫu | Tổng số mẫu âm thanh trong mirror đã dọn dẹp |
| **Số giờ Train** | `~100` giờ | |
| **Số giờ Validation** | `0` giờ | |
| **Số giờ Test** | `0` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Nhiều người nói (Multi-speaker) |
| **Độ dài trung bình mỗi file** | `~13.8` giây | Ước lượng |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav / Parquet | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Tần số mẫu chuẩn |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Thu âm trong môi trường gia đình hoặc văn phòng tương đối yên tĩnh, có thể có ít tiếng vang phòng hoặc nhiễu thiết bị nhỏ.
* **Miền ngữ cảnh (Domain):** Giọng đọc sách, mệnh lệnh ngắn, hội thoại đời sống.
* **Phương ngữ (Dialects):** Gồm các giọng Bắc, Trung, Nam.

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `sentence` | Nhãn văn bản (transcription) | String |
| `id` | Mã định danh mẫu | String |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
ds = load_dataset("doof-ferb/fpt_fosd", split="train")
print(ds[0])  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn do con người gõ (Human-labeled). Ở bản mirror của doof-ferb, các từ vô nghĩa và file âm thanh bị lỗi/không có transcription đã được lọc bỏ.
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho FPT FOSD:**
1. **Kiểm tra lại nhãn đã dọn dẹp:** Bản mirror doof-ferb đã xóa non-sense strings và file lỗi, nhưng cần double-check xem có còn sót mẫu có transcript trống hoặc transcript chỉ chứa ký tự đặc biệt không.
2. **Tách tập validation:** Dataset gốc chỉ có `train` split (100h). Cần tự tách ra validation set (khuyến nghị tỉ lệ 95/5 hoặc 97/3) **trước khi** đưa vào pipeline training.
3. **Xử lý format sentence:** Cột transcript là `sentence` (không phải `text` hay `transcription` như các dataset khác) — lưu ý mapping đúng khi viết data loader thống nhất.
4. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " '`)
- [ ] **Number → Text:** Chuyển số → chữ viết
- [ ] **Special Characters:** Xóa ký tự đặc biệt còn sót sau dọn dẹp mirror
- [ ] **Foreign Words:** Chuẩn hóa từ tiếng Anh lẫn trong transcript theo từ điển chung
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt
- [ ] **Train/Val Split:** Đã tách validation set

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> FPT FOSD thuộc nhóm **core labeled datasets** (~100 giờ, nhãn do người gõ). Trong baseline Zipformer-30M-RNNT-6000h, bộ này đóng góp vào khối ~1,000 giờ labeled. Thuộc nhóm **phase 1 training** — dữ liệu sạch nhất, ưu tiên đưa vào đầu tiên.
>
> **Ưu điểm:**
> Nhãn do con người gõ — chất lượng cao. Bản mirror đã dọn dẹp sạch file lỗi. Dung lượng vừa phải (~10-15GB) — dễ tải và xử lý. License CC-BY-4.0 mở hoàn toàn. Giọng đọc chuẩn, dễ học cho mô hình giai đoạn đầu.
>
> **Nhược điểm & Rủi ro:**
> Không chia sẵn tập validation/test — phải tự tách. Chỉ có 100 giờ — không đủ lớn để training đơn lẻ. Cột transcript dùng tên `sentence` (khác với `text` hoặc `transcription` của các dataset khác) — cần chú ý khi viết unified data loader.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 1 — Core training (ưu tiên cao):** FPT FOSD nên nằm trong batch đầu tiên cùng VLSP2020, VietBud500, VietSpeech. Nhãn sạch và giọng đọc chuẩn giúp mô hình cải tiến hội tụ nhanh hơn ở giai đoạn đầu khi train from scratch.
> - **Schema mapping:** Mapping `sentence` → `text` trong unified data loader để đồng bộ với các dataset khác.
> - **Validation set:** Tách 5% (~5h) làm validation set. Sử dụng validation loss để giám sát quá trình training, không dùng để tính WER (WER chính nên dùng FLEURS test set).

---
