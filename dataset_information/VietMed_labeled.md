# DATASET METADATA PROFILE: VietMed Labeled (VietMed_labeled)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `doof-ferb/VietMed_labeled` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | Khai Le-Duc et al. (Mirror bởi doof-ferb) |
| **Giấy phép (License)** | CC-BY-NC-ND-4.0 |
| **Bài báo / Nguồn gốc** | [VietMed Paper](https://arxiv.org/abs/2309.00845) |
| **Dung lượng tải về (Download)** | `...` GB (Nhỏ gọn, chỉ chứa tập labeled) |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~16` giờ | Phần dữ liệu đã gán nhãn |
| **Tổng số mẫu (Samples)** | `~9,200` mẫu | Tổng số mẫu âm thanh trong tập gán nhãn |
| **Số giờ Train** | `...` giờ | |
| **Số giờ Validation** | `...` giờ | |
| **Số giờ Test** | `...` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Bác sĩ, bệnh nhân thực tế |
| **Độ dài trung bình mỗi file** | `~6.2` giây | Ước lượng |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz / `8000` Hz | Cần lưu ý một số file y tế thu qua tổng đài/telehealth có thể là 8kHz |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Telehealth (tư vấn y tế từ xa), ghi âm trực tiếp tại phòng khám (clinical setting). Chứa tiếng ồn nền y tế, tiếng còi xe, tiếng thở, chất lượng âm thanh từ micro điện thoại/thiết bị y tế.
* **Miền ngữ cảnh (Domain):** Y khoa (Medical Domain, clinical conversations, tư vấn bệnh lý). Bao trùm toàn bộ các nhóm bệnh ICD-10.
* **Phương ngữ (Dialects):** Đầy đủ 3 miền Bắc, Trung, Nam.

---

## V. CẤU TRÚC DỮ LIỆU (DATA SCHEMA)

| Cột trong Dataset | Ý nghĩa | Kiểu dữ liệu |
| :--- | :--- | :--- |
| `audio` | Dữ liệu âm thanh | Audio (dict chứa array, sampling_rate, path) |
| `text` | Nhãn văn bản (transcription) | String |
| `speaker` | Mã định danh người nói | String |

**Lệnh load mẫu:**
```python
from datasets import load_dataset
ds = load_dataset("doof-ferb/VietMed_labeled", split="train")
print(ds[0])  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn chuẩn do các chuyên gia y tế hoặc người có chuyên môn gõ/kiểm duyệt (Human-labeled)
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho VietMed Labeled:**
1. **Xây dựng từ điển y khoa:** Transcript chứa rất nhiều thuật ngữ y học đa ngữ (`paracetamol`, `acetaminophen`, `xơ vữa động mạch`, `hemoglobin`, `huyết áp tâm thu`). Cần xây dựng từ điển mapping: thuật ngữ Latinh/Anh → phiên âm tiếng Việt hoặc giữ nguyên nhất quán.
2. **Xử lý mã ICD-10 và viết tắt y khoa:** Các mã như `ICD-10`, `WHO`, `BMI`, `SpO2`, `ECG` xuất hiện thường xuyên. Cần quy ước: đọc nguyên dạng chữ cái (ví dụ: `bê-em-ai`) hoặc giữ nguyên ký tự.
3. **Xử lý liều lượng thuốc:** Các chuỗi như `500mg`, `2 viên/ngày`, `0.5ml` cần chuyển thành dạng đọc (`năm trăm mi-li-gam`, `hai viên mỗi ngày`).
4. **Lọc chất lượng audio:** Một số file telehealth thu qua điện thoại có SNR rất thấp. Cần lọc bỏ các mẫu có SNR < ngưỡng hoặc resample từ 8kHz lên 16kHz nếu cần.
5. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " '`)
- [ ] **Number → Text:** Chuyển số → chữ viết (đặc biệt liều lượng thuốc, đơn vị y khoa)
- [ ] **Special Characters:** Xóa ký tự đặc biệt, giữ lại viết tắt y khoa theo quy ước
- [ ] **Foreign Words:** Chuẩn hóa thuật ngữ y học Latinh/Anh/Pháp theo từ điển y khoa
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt
- [ ] **Medical Dictionary:** Đã áp dụng từ điển chuẩn hóa thuật ngữ y khoa

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> VietMed Labeled thuộc nhóm **dữ liệu domain-specific nhỏ** (~16 giờ labeled). Trong baseline Zipformer-30M-RNNT-6000h, bộ này đóng góp vào khối ~1,000 giờ labeled nhưng chủ yếu mang giá trị domain adaptation. Nên dùng ở **phase 3 — domain fine-tuning** nếu mục tiêu bao gồm ứng dụng y tế.
>
> **Ưu điểm:**
> Dataset y tế tiếng Việt duy nhất và chất lượng nhất hiện tại. Chứa thuật ngữ chuyên ngành y khoa, tên thuốc, tên bệnh theo ICD-10 — giá trị cực cao cho domain adaptation y tế. Nhãn do chuyên gia kiểm duyệt — độ chính xác cao.
>
> **Nhược điểm & Rủi ro:**
> Số lượng giờ labeled rất ít (~16 giờ). Thuật ngữ Anh/Pháp/Latin viết theo kiểu Việt hóa hoặc nguyên bản gây khó cho normalization. Chất lượng audio một số file telehealth thấp (nhiễu kênh điện thoại, 8kHz). Vocabulary rất chuyên biệt — nếu trộn vào phase 1 có thể gây bias domain.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 3 — Domain fine-tuning (tùy chọn):** Chỉ đưa VietMed vào giai đoạn cuối (domain adaptation) sau khi mô hình đã hội tụ tốt trên dữ liệu tổng quát. Nếu mục tiêu KHÔNG bao gồm y tế, có thể bỏ qua bộ này.
> - **Từ điển chuyên ngành:** Bắt buộc xây dựng từ điển chuẩn hóa thuật ngữ y khoa **trước khi** đưa vào pipeline. Đây là bước tốn thời gian nhất.
> - **Audio quality gate:** Lọc nghiêm ngặt chất lượng audio (loại bỏ file 8kHz hoặc SNR quá thấp) để tránh "nhiễm" acoustic noise vào mô hình ở phase cuối.

---
