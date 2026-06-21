# DATASET METADATA PROFILE: VietBud500 (viet_bud500)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `linhtran92/viet_bud500` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | VietAI |
| **Giấy phép (License)** | Apache-2.0 |
| **Bài báo / Nguồn gốc** | [Viet-Bud500 Github](https://github.com/vietai/viet-bud500) |
| **Dung lượng tải về (Download)** | `~100` GB |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~500` giờ | |
| **Tổng số mẫu (Samples)** | `~649,000` mẫu | Tổng số mẫu âm thanh trên các split |
| **Số giờ Train** | `...` giờ | |
| **Số giờ Validation** | `...` giờ | |
| **Số giờ Test** | `...` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Nhiều người nói, đa dạng độ tuổi |
| **Độ dài trung bình mỗi file** | `~2.7` giây | Ước lượng dựa trên số lượng mẫu và tổng số giờ |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav / Parquet | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Tần số mẫu chuẩn cho ASR |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Đa dạng: từ studio đến thu âm qua thiết bị cá nhân di động, các bài phát biểu, podcast.
* **Miền ngữ cảnh (Domain):** Rất đa dạng: Sách nói, Phật giáo (các bài giảng pháp), podcast, đời sống, khoa học xã hội.
* **Phương ngữ (Dialects):** Đa dạng phương ngữ Bắc, Trung, Nam.

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
ds = load_dataset("linhtran92/viet_bud500", split="train", streaming=True)
sample = next(iter(ds))
print(sample)  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn chuẩn do con người kiểm duyệt kết hợp với một phần hậu xử lý tự động (Human-labeled/Verified)
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho VietBud500:**
1. **Xử lý thuật ngữ Phật giáo:** Transcript chứa nhiều thuật ngữ Phật giáo Hán-Việt (`bồ đề`, `bát nhã`, `niết bàn`, `a di đà`). Cần giữ nguyên dạng phiên âm Hán-Việt chuẩn, không Latinh hóa.
2. **Xử lý giọng đọc sách nói:** Nhiều mẫu là audiobook — transcript có thể chứa dấu chấm lửng `...`, dấu gạch ngang dài `—`, hoặc ký hiệu đánh số chương/phần (`Chương 1:`, `Phần II.`). Cần loại bỏ hoặc chuẩn hóa.
3. **Lọc theo độ dài:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự. Đồng thời loại bỏ các file audio < 1 giây (lỗi cắt đoạn).
4. **Xử lý số liệu kinh Phật:** Các con số như `108 hạt`, `500 vị`, `84000 pháp môn` cần chuyển thành dạng chữ viết chuẩn.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " ' — …`)
- [ ] **Number → Text:** Chuyển số → chữ viết (đặc biệt số liệu kinh Phật, số thứ tự chương)
- [ ] **Special Characters:** Xóa ký tự đặc biệt, ký hiệu đánh số chương/phần
- [ ] **Foreign Words:** Giữ nguyên thuật ngữ Hán-Việt, chuẩn hóa từ tiếng Anh
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> VietBud500 là một trong những **core labeled datasets** (~500 giờ, nhãn do người kiểm duyệt). Trong baseline Zipformer-30M-RNNT-6000h, bộ này đóng góp trực tiếp vào khối ~1,000 giờ labeled. Đây là dataset thuộc nhóm **phase 1 training** (dữ liệu sạch, labeled).
>
> **Ưu điểm:**
> Quy mô lớn (500 giờ), nhãn do người kiểm duyệt — chất lượng cao. Đa dạng vùng miền (Bắc, Trung, Nam). Từ vựng phong phú bao gồm cả thuật ngữ Hán-Việt chuyên ngành. Giọng đọc rõ ràng, mạch lạc.
>
> **Nhược điểm & Rủi ro:**
> Dung lượng tải về lớn (~100GB). Gated dataset — cần đồng ý điều khoản trên Hugging Face. Nội dung thiên về sách nói/giảng pháp nên vocabulary có thể skewed về domain Phật giáo. Một số file rất ngắn có thể gây lỗi padding khi batch training.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 1 — Core training:** VietBud500 nên nằm trong nhóm dataset đầu tiên (cùng VLSP2020, FPT FOSD) để mô hình học được acoustic model cơ bản với nhãn sạch.
> - **Augmentation:** Áp dụng noise injection + low-bitrate simulation vì dữ liệu gốc khá sạch — cần tăng robustness cho mô hình khi deploy thực tế.
> - **Lưu ý streaming:** Do dung lượng 100GB, nên sử dụng `lhotse` với `webdataset` format hoặc load theo kiểu `lazy` để tránh OOM RAM khi chuẩn bị feature.

---
