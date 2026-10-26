# KỊCH BẢN DEMO SỐNG BẢO VỆ ĐỒ ÁN (DEMO REHEARSAL SCRIPT)
**Thời lượng dự kiến: 10 - 15 phút | Nhóm 03 Sinh viên**

---

## 🎭 Phân Vai & Chuẩn Bị
* **SV1 (Data Architect & CRUD Lead)**: Phụ trách demo nhập liệu bệnh án đa chuyên khoa trên Web/Streamlit, giải trình mô hình NoSQL.
* **SV2 (Advanced Query Specialist)**: Phụ trách demo kích hoạt báo cáo thống kê y tế và giải thích câu lệnh MongoDB Aggregation Pipeline & Index.
* **SV3 (Fullstack Integrator & DB Tester)**: Phụ trách trình chiếu MongoDB Compass để đối chiếu cấu trúc Document, thực hiện thao tác Backup/Restore và điều phối buổi demo.

---

## 🎬 Diễn Biến Kịch Bản 4 Bước Bảo Vệ

### Bước 1: Demo Khám Bệnh Đa Chuyên Khoa & Chứng Minh Schema-less (3-4 phút)
* **SV1 thao tác**:
  1. Mở giao diện `http://localhost:8501` (Trang: `📋 Khám Bệnh Động`).
  2. Chọn một bệnh nhân bất kỳ trong danh sách.
  3. Chọn **Khoa Tim Mạch**: Nhập các chỉ số huyết áp (160/100), nhịp tim (95), kết quả ECG ("ST chênh xuống"), EF (52%), kê đơn thuốc và bấm **"Lưu Bệnh Án"**.
  4. Tiếp tục chọn **Khoa Da Liễu**: Form lập tức chuyển sang các trường vị trí tổn thương (Mặt, Cánh tay), loại tổn thương ("Mụn nước rải rác"), mức độ ngứa ("Nặng"), kết quả Patch test, bấm **"Lưu Bệnh Án"**.
* **SV3 thao tác ngay sau đó**:
  1. Chuyển màn hình sang **MongoDB Compass**, mở collection `medical_records`.
  2. Mở 2 document vừa tạo ở chế độ JSON View chiếu lên màn hình máy chiếu.
  3. **Thuyết minh**: *"Kính thưa Thầy/Cô, như có thể thấy trên Compass, cả hai hồ sơ của Khoa Tim Mạch và Da Liễu đều nằm chung trong collection `medical_records`. Hồ sơ Tim Mạch chứa object `blood_pressure`, `ecg_result` còn hồ sơ Da Liễu chứa mảng `lesion_locations` và `pruritus_level`. MongoDB hoàn toàn không bắt buộc các trường phải đồng nhất như SQL, chứng minh tính linh hoạt tuyệt đối của mô hình Document."*

---

### Bước 2: Kích Hoạt Báo Cáo Dịch Tễ & Giải Thích Aggregation (4-5 phút)
* **SV2 thao tác**:
  1. Chuyển sang Trang `📊 Thống Kê Y Tế`.
  2. Bấm nút **"KÍCH HOẠT BÁO CÁO THỐNG KÊ DỊCH TỄ / BỆNH LÝ"**.
  3. Trình bày 3 biểu đồ trực quan hóa dữ liệu trên quy mô **18.186 bệnh án** và **10.120 bệnh nhân**:
     - **Biểu đồ 1 (Chuyên khoa)**: RANG_HAM_MAT 6.066 ca, TIM_MACH 6.065 ca, DA_LIEU 6.055 ca. Mở phần *Xem câu lệnh Pipeline 1* giải thích `$match` lọc `visit_date` → `$group` theo `department` → `$cond` đếm ca tái khám → `$size` đếm lượt thuốc (không cần `$unwind`).
     - **Biểu đồ 2 (Độ tuổi)**: 4 nhóm `0-18` (3.856 ca), `19-40` (4.852 ca), `41-60` (4.533 ca), `60+` (4.945 ca). Giải thích `$lookup` nối với collection `patients` (phải `$convert` chuỗi `patient_id` sang ObjectId), `$dateDiff` tính tuổi tại ngày khám và `$switch` phân nhóm.
     - **Biểu đồ 3 (Tái khám)**: 10.120 bệnh nhân từng khám, 5.041 bệnh nhân tái khám, tỷ lệ **49,81%**. Giải thích `$group` theo `patient_id` rồi `$facet` chạy song song: một nhánh `$bucket` (5.079 người khám 1 lần, 4.532 người 2-3 lần, 509 người >3 lần), một nhánh tính tổng và tỷ lệ.
  4. Mở `backend/app/services/analytics_service.py` chỉ rõ 3 hàm tương ứng; Pipeline 3 tính `revisit_rate_percent` ngay trong `$project`, không chia bằng Python.
  5. Mở MongoDB Compass → `medispace_db.medical_records` → tab **Aggregations**, dán pipeline 1 để đối chiếu kết quả trực tiếp.
  6. Trình chiếu kết quả từ `python scripts/create_indexes.py` trên tập 18.186 bản ghi:
     - Trước index: `SORT <- COLLSCAN`, `totalDocsExamined = 18186`, thời gian `27 ms`.
     - Sau Compound Index `{ department: 1, visit_date: -1 }`: `FETCH <- IXSCAN`, `totalDocsExamined = 6038` (giảm 66,8%), thời gian `11 ms` (giảm 59,3%), không còn stage `SORT`.
     - Mở tab **Explain Plan** trên Compass để xác nhận `IXSCAN` nếu giảng viên yêu cầu.
  7. Nhấn mạnh việc tối ưu hiệu năng: Với tập dữ liệu lớn hơn 18.000 documents, Compound Index chuẩn quy tắc ESR giúp MongoDB giảm hơn 66% số documents phải đọc, loại bỏ hoàn toàn stage sắp xếp trong RAM, và tăng tốc độ truy vấn hơn 2.4 lần.
  8. Chi tiết từng stage và bảng số liệu đầy đủ nằm trong `docs/aggregation_explained.md`.

---

### Bước 3: Thao Tác Backup & Restore Trực Tiếp Trên GUI Tool (3 phút)
* **SV3 thao tác**:
  1. Mở MongoDB Compass, vào collection `medical_records`.
  2. Bấm **Collection** $\rightarrow$ **Export Collection** $\rightarrow$ Xuất ra file `medical_records_backup.json` (khoảng 18.186 documents).
  3. Giả lập sự cố: Chọn xóa 1 vài bản ghi hoặc Drop collection.
  4. Quay lại giao diện web tải lại trang để thấy số lượng ca bệnh bị mất hoặc giảm đi.
  5. Quay lại Compass, bấm **Add Data** $\rightarrow$ **Import JSON or CSV** $\rightarrow$ Chọn file vừa xuất và nạp lại.
  6. Tải lại trang web: Toàn bộ dữ liệu hiển thị trở lại đầy đủ, chứng minh tính toàn vẹn của quy trình sao lưu và phục hồi.

---

### Bước 4: Tổng Kết & Trả Lời Câu Hỏi Của Hội Đồng (2-3 phút)
* **Cả nhóm**:
  - Tóm tắt lại: Đã triển khai và nạp thành công bộ dữ liệu thực tế gồm **10.120 bệnh nhân** và **18.186 hồ sơ bệnh án đa chuyên khoa** (đáp ứng và vượt xa định mức đồ án môn học).
  - Sẵn sàng trả lời các câu hỏi chuyên sâu của Hội đồng về thiết kế schema, sharding, replica set hoặc so sánh MongoDB với CouchDB / RDBMS.
