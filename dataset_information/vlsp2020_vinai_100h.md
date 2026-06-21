# DATASET METADATA PROFILE: VLSP 2020 VinAI 100h (vlsp2020_vinai_100h)

---

## I. THÔNG TIN CHUNG (GENERAL INFO)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Hugging Face Repository** | `doof-ferb/vlsp2020_vinai_100h` |
| **Subset / Config** | `default` |
| **Tác giả / Tổ chức** | VinBigData / VinAI / VLSP |
| **Giấy phép (License)** | CC-BY-4.0 |
| **Bài báo / Nguồn gốc** | [VLSP 2020 ASR Challenge](https://huggingface.co/datasets/doof-ferb/vlsp2020_vinai_100h) |
| **Dung lượng tải về (Download)** | `...` GB |

---

## II. THỐNG KÊ TỔNG QUAN (DATASET STATISTICS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Tổng số giờ (Duration)** | `~100` giờ | Tính trên toàn bộ tập dữ liệu |
| **Tổng số mẫu (Samples)** | `56,400` mẫu | Số lượng mẫu âm thanh thực tế trong mirror |
| **Số giờ Train** | `~100` giờ | |
| **Số giờ Validation** | `0` giờ | |
| **Số giờ Test** | `0` giờ | |
| **Số lượng người nói (Speakers)** | `...` người | Nhiều người nói (Multi-speaker) |
| **Độ dài trung bình mỗi file** | `~6.4` giây | Ước lượng |

---

## III. ĐẶC TÍNH ÂM THANH (AUDIO SPECIFICATIONS)

| Tiêu chí | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Định dạng gốc (Format)** | Wav | |
| **Tần số mẫu (Sample Rate)** | `16000` Hz | Đã resample |
| **Kênh (Channels)** | Mono | 1 kênh |
| **Bit Depth** | 16-bit | |

---

## IV. THUỘC TÍNH NGỮ CẢNH (DOMAIN & ENVIRONMENT)

* **Ngôn ngữ (Language):** Tiếng Việt (`vi`)
* **Môi trường thu âm:** Thu âm qua điện thoại di động, máy ghi âm hoặc máy tính cá nhân ở các môi trường sinh hoạt hàng ngày (nhà ở, văn phòng). Có thể lẫn một số tạp âm nền nhẹ.
* **Miền ngữ cảnh (Domain):** Đọc tin tức, hội thoại sinh hoạt hàng ngày, câu lệnh điều khiển.
* **Phương ngữ (Dialects):** Đầy đủ 3 miền Bắc, Trung, Nam.

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
ds = load_dataset("doof-ferb/vlsp2020_vinai_100h", split="train")
print(ds[0])  # Xem cấu trúc 1 mẫu
```

---

## VI. QUY TRÌNH CHUẨN HÓA VĂN BẢN (TEXT NORMALIZATION STATUS)

* **Trạng thái nhãn gốc:** Nhãn do con người ghi nhận và đối soát (Human-labeled). Bản mirror đã được tiền xử lý loại bỏ một số token lỗi như `<unk>`.
* **Encoding transcript:** UTF-8

**Pipeline tiền xử lý cụ thể cho VLSP2020 VinAI 100h:**
1. **Kiểm tra token đặc biệt còn sót:** Bản mirror đã xóa `<unk>` nhưng cần kiểm tra thêm các token khác như `<noise>`, `<silence>`, `<laugh>`, `[UNKNOWN]` có thể còn sót.
2. **Tách tập validation:** Dataset gốc chỉ có `train` split (100h). Cần tự tách validation set (khuyến nghị tỉ lệ 95/5) **trước khi** đưa vào pipeline training.
3. **Xử lý format sentence:** Cột transcript là `sentence` — lưu ý mapping đúng trong unified data loader.
4. **Xử lý transcript đã merge:** Bản mirror đã merge các file transcript rời lại — cần kiểm tra alignment audio-text đúng sau khi merge.
5. **Lọc theo độ dài transcript:** Áp dụng bộ lọc baseline: loại bỏ mẫu có transcript < 10 ký tự hoặc > 1000 ký tự.

**Checklist chuẩn hóa:**
- [ ] **Lowercase:** Chuyển toàn bộ về chữ thường
- [ ] **Punctuation:** Xóa dấu câu (`. , ? ! ; : - " '`)
- [ ] **Number → Text:** Chuyển số → chữ viết
- [ ] **Special Characters:** Xóa ký tự đặc biệt, token lỗi (`<unk>`, `<noise>`, etc.)
- [ ] **Foreign Words:** Chuẩn hóa từ tiếng Anh lẫn trong transcript theo từ điển chung
- [ ] **Whitespace:** Chuẩn hóa khoảng trắng thừa → single space
- [ ] **Unicode NFC:** Chuẩn hóa Unicode dạng NFC cho dấu tiếng Việt
- [ ] **Train/Val Split:** Đã tách validation set
- [ ] **Token Cleanup:** Đã xóa sạch các token đặc biệt (`<unk>`, `<noise>`, etc.)

---

## VII. NHẬN XÉT (ENG LOGS)

> **Vai trò trong Pipeline:**
> VLSP2020 VinAI 100h là **dataset benchmark kinh điển** của ASR tiếng Việt — xuất phát từ cuộc thi VLSP 2020. Trong baseline Zipformer-30M-RNNT-6000h (tác giả hynt đã thắng giải nhất VLSP 2025 với kiến trúc này), VLSP2020 nằm trong nhóm ~1,000 giờ labeled. Thuộc nhóm **phase 1 training**.
>
> **Ưu điểm:**
> Benchmark kinh điển — chất lượng nhãn cao, dữ liệu sạch. Nhãn do chuyên gia đối soát. Dung lượng vừa phải. License CC-BY-4.0 mở hoàn toàn. Kết quả WER trên VLSP2020 test set được cộng đồng dùng rộng rãi để so sánh các mô hình ASR.
>
> **Nhược điểm & Rủi ro:**
> Không chia sẵn tập validation/test — phải tự tách. Chỉ có 100 giờ. Cột transcript dùng tên `sentence`. Cần kiểm tra kỹ alignment audio-text do transcript đã được merge.
>
> **Chiến lược với Improved Zipformer (train from scratch):**
> - **Phase 1 — Core training (ưu tiên cao):** VLSP2020 nên nằm cùng batch đầu tiên với FPT FOSD, VietBud500, VietSpeech. Nhãn sạch giúp kiến trúc cải tiến hội tụ nhanh mà không cần checkpoint.
> - **Schema mapping:** Mapping `sentence` → `text` trong unified data loader (giống FPT FOSD).
> - **Validation set:** Tách 5% (~5h) làm validation set nội bộ. WER chính thức vẫn nên dùng FLEURS test set để so sánh trực tiếp với baseline.
> - **Lưu ý so sánh:** Tác giả baseline hynt đã dùng VLSP2020 trong cả training lẫn đánh giá (trên VLSP test set riêng). Nếu bạn muốn so sánh công bằng, hãy tách riêng VLSP test set hoặc dùng FLEURS test set làm benchmark chính.

---
