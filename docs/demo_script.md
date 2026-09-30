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
  3. Trình bày 3 biểu đồ trực quan hóa dữ liệu:
     - **Biểu đồ 1 (Chuyên khoa)**: Số ca khám và tỷ lệ tái khám theo từng khoa. Mở phần *Xem câu lệnh Pipeline 1* giải thích stage `$group` và toán tử điều kiện `$cond`.
     - **Biểu đồ 2 (Độ tuổi)**: Tỷ lệ mắc bệnh theo các nhóm tuổi (Nhi, Thanh niên, Trung niên, Cao tuổi). Giải thích stage `$lookup` nối với collection `patients`, tính tuổi từ năm sinh và phân loại bằng `$switch`.
     - **Biểu đồ 3 (Tái khám)**: Tần suất tái khám qua `$facet` và `$bucket`.
  4. Trình chiếu kết quả đo lường chỉ mục từ script `create_indexes.py` (chứng minh tốc độ truy vấn tăng vọt từ `COLLSCAN` sang `IXSCAN` với Compound Index).

---

### Bước 3: Thao Tác Backup & Restore Trực Tiếp Trên GUI Tool (3 phút)
* **SV3 thao tác**:
  1. Mở MongoDB Compass, vào collection `medical_records`.
  2. Bấm **Collection** $\rightarrow$ **Export Collection** $\rightarrow$ Xuất ra file `medical_records_backup.json`.
  3. Giả lập sự cố: Chọn xóa 1 vài bản ghi hoặc Drop collection.
  4. Quay lại giao diện web tải lại trang để thấy số lượng ca bệnh bị mất hoặc giảm đi.
  5. Quay lại Compass, bấm **Add Data** $\rightarrow$ **Import JSON or CSV** $\rightarrow$ Chọn file vừa xuất và nạp lại.
  6. Tải lại trang web: Toàn bộ dữ liệu hiển thị trở lại đầy đủ, chứng minh tính toàn vẹn của quy trình sao lưu và phục hồi.

---

### Bước 4: Tổng Kết & Trả Lời Câu Hỏi Của Hội Đồng (2-3 phút)
* **Cả nhóm**:
  - Tóm tắt lại: Đã đạt đầy đủ định mức $\ge 100$ bệnh nhân và $\ge 150$ hồ sơ bệnh án đa chuyên khoa.
  - Sẵn sàng trả lời các câu hỏi chuyên sâu của Hội đồng về thiết kế schema, sharding, replica set hoặc so sánh MongoDB với CouchDB / RDBMS.
