# BẢNG PHÂN CÔNG NHIỆM VỤ & THEO DÕI TIẾN ĐỘ (NHÓM 03 SINH VIÊN)
**Đồ án:** Hệ Thống Quản Lý Hồ Sơ Bệnh Án Điện Tử Tại Phòng Khám  
**Hệ quản trị CSDL:** MongoDB  
**Thang điểm đánh giá:** 10.0  

---

## 👥 1. BẢNG TỔNG QUAN PHÂN CÔNG VAI TRÒ & BAREM ĐIỂM

| Thành viên | Vai trò phụ trách | Trọng số barem điểm liên quan | Nhánh Git đề xuất |
| :--- | :--- | :--- | :--- |
| **SV1** | **Data Architect & CRUD Lead** | **3.75 điểm**<br>• 1.25đ: Thiết kế Schema Document đa chuyên khoa & giải trình NoSQL.<br>• 2.50đ: Chức năng CRUD Bệnh nhân, Bệnh án & Đơn thuốc. | `feat/sv1-db-models`<br>`feat/sv1-patient-crud`<br>`feat/sv1-record-crud` |
| **SV2** | **Advanced Query Specialist** | **2.50 điểm**<br>• 2.50đ: 3 Aggregation Pipelines (Khoa, Độ tuổi, Tái khám) + Tối ưu hóa chỉ mục (Indexes). | `feat/sv2-dept-stats`<br>`feat/sv2-age-revisit`<br>`feat/sv2-indexes` |
| **SV3** | **Fullstack Integrator & DB Tester** | **3.75 điểm**<br>• 1.00đ: Bộ Dummy Data đạt định mức $\ge 100$ BN, $\ge 100$ Bệnh án.<br>• 1.25đ: Giao diện nhập bệnh án động (Streamlit).<br>• 1.50đ: Quy trình Backup/Restore trên GUI Tool (Compass) & điều phối demo. | `feat/sv3-dummy-data`<br>`feat/sv3-dynamic-ui`<br>`docs/sv3-backup-demo` |

---

## 📝 2. CHI TIẾT NHIỆM VỤ CỤ THỂ CHO TỪNG THÀNH VIÊN

### 👤 SINH VIÊN 1: Data Architect & CRUD Lead
* **Mục tiêu**: Làm chủ thiết kế dữ liệu Schema-less của MongoDB và xây dựng trọn bộ API CRUD cốt lõi.
* **Danh sách đầu việc chi tiết**:
  1. [ ] Thiết kế cấu trúc Document linh hoạt cho hồ sơ bệnh án đa chuyên khoa (Tim Mạch, Da Liễu, Răng - Hàm - Mặt) và mảng đơn thuốc lồng (`prescriptions`).
  2. [ ] Viết Pydantic models cho Bệnh nhân (`Patient`) và Bệnh án (`MedicalRecord`).
  3. [ ] Xây dựng dịch vụ `PatientService`:
     - Thêm mới bệnh nhân (kiểm tra trùng mã `patient_code`).
     - Lấy danh sách bệnh nhân có phân trang (`skip`, `limit`) và tìm kiếm theo Tên / SĐT / Mã BN.
     - Cập nhật và xóa hồ sơ bệnh nhân.
  4. [ ] Xây dựng dịch vụ `RecordService`:
     - Tạo phiếu khám bệnh lồng ghép dữ liệu chuyên khoa (`specialty_data`) và đơn thuốc.
     - Lấy lịch sử khám theo bệnh nhân (`patient_id`) và lọc theo chuyên khoa (`department`).
  5. [ ] Viết tài liệu giải trình sự cần thiết của CSDL Document đối với dữ liệu y tế không đồng nhất (nội dung báo cáo mục 1.1).
  6. [ ] **Nhiệm vụ trong buổi Demo bảo vệ**: Thao tác tạo 2 bệnh án thuộc 2 khoa khác nhau trên giao diện để SV3 chiếu Compass chứng minh tính Schema-less.
* **Các file phụ trách chính**:
  - `backend/app/models/patient.py`
  - `backend/app/models/record.py`
  - `backend/app/services/patient_service.py`
  - `backend/app/services/record_service.py`
  - `backend/app/api/v1/patients.py`
  - `backend/app/api/v1/records.py`
  - `docs/db_design.md`

---

### 👤 SINH VIÊN 2: Advanced Query Specialist
* **Mục tiêu**: Khai thác tối đa sức mạnh tính toán của MongoDB Aggregation Framework và tối ưu hóa hiệu năng truy vấn.
* **Danh sách đầu việc chi tiết**:
  1. [ ] **Aggregation Pipeline 1 (Thống kê chuyên khoa)**:
     - Dùng `$group` theo `department`.
     - Tính tổng số ca khám, số ca cần hẹn tái khám (`$cond`), và đếm số bác sĩ tham gia (`$addToSet` + `$size`).
  2. [ ] **Aggregation Pipeline 2 (Phân tích theo nhóm tuổi)**:
     - Nối dữ liệu sang `patients` bằng `$lookup` và `$unwind`.
     - Tính tuổi từ năm sinh và phân loại bằng toán tử điều kiện `$switch` (Nhi, Thanh niên, Trung niên, Cao tuổi).
     - Gom nhóm đếm số ca bệnh theo `{ age_group, department }`.
  3. [ ] **Aggregation Pipeline 3 (Tần suất & Tỷ lệ tái khám)**:
     - Gom nhóm theo `patient_id` tính số lần khám của từng người.
     - Sử dụng `$facet` chia 2 luồng tính toán song song:
       - `summary`: Tính tổng bệnh nhân, số người tái khám ($\ge 2$ lần), số người khám 1 lần, tỷ lệ tái khám (%).
       - `distribution`: Phân khoảng số lượt khám bằng `$bucket`.
  4. [ ] **Tối ưu hóa chỉ mục (Indexes)**:
     - Tạo Single Index: `patient_code` (unique), `patient_id`.
     - Tạo Compound Index: `{ department: 1, visit_date: -1 }`.
     - Chạy script đo lường hiệu năng bằng `.explain("executionStats")` trước và sau index (chứng minh bước nhảy từ `COLLSCAN` sang `IXSCAN`).
  5. [ ] **Nhiệm vụ trong buổi Demo bảo vệ**: Kích hoạt báo cáo thống kê dịch tễ trên giao diện, giải thích ý nghĩa từng stage trong câu lệnh Aggregation và trình chiếu chỉ số tối ưu của index.
* **Các file phụ trách chính**:
  - `backend/app/services/analytics_service.py`
  - `backend/app/api/v1/analytics.py`
  - `scripts/create_indexes.py`
  - `docs/aggregation_explained.md`

---

### 👤 SINH VIÊN 3: Fullstack Integrator & DB Tester
* **Mục tiêu**: Đảm bảo toàn vẹn dữ liệu mẫu đạt chuẩn định mức, xây dựng UI trực quan và làm chủ quy trình Backup/Restore.
* **Danh sách đầu việc chi tiết**:
  1. [ ] **Xây dựng Script nạp dữ liệu mẫu (`seed_data.py`)**:
     - Sinh tối thiểu **100+ Document hồ sơ bệnh nhân** với thông tin tự nhiên (họ tên tiếng Việt, ngày sinh, địa chỉ, nhóm máu, tiền sử dị ứng).
     - Sinh tối thiểu **100+ Lượt khám bệnh** phân bổ đều vào $\ge 3$ chuyên khoa (Tim Mạch, Da Liễu, Răng - Hàm - Mặt) với dữ liệu trường lâm sàng phong phú.
     - Đảm bảo tỷ lệ tái khám thực tế (nhiều bệnh nhân có $\ge 2$ lượt khám).
  2. [ ] **Xây dựng Giao diện người dùng (Streamlit UI)**:
     - Trang 1: Quản lý danh sách bệnh nhân và form thêm mới.
     - Trang 2: **Form nhập bệnh án động (Dynamic Form)** - Chọn chuyên khoa nào thì giao diện tự động thay đổi các trường dữ liệu lâm sàng đặc thù của chuyên khoa đó.
     - Trang 3: Dashboard biểu đồ trực quan hóa dữ liệu thống kê từ các pipeline của SV2.
  3. [ ] **Quy trình Backup & Restore CSDL**:
     - Soạn thảo tài liệu và thực hành thành thạo thao tác Export/Import JSON trên **MongoDB Compass**.
     - Xây dựng script sao lưu phục hồi dòng lệnh `mongodump` và `mongorestore`.
  4. [ ] **Nhiệm vụ trong buổi Demo bảo vệ**:
     - Điều phối máy chiếu và trình chiếu kịch bản demo.
     - Mở MongoDB Compass soi cấu trúc JSON Document sau khi SV1 nhập bệnh án.
     - Thao tác trực tiếp Backup $\rightarrow$ Xóa thử dữ liệu $\rightarrow$ Restore phục hồi toàn vẹn trước Hội đồng.
* **Các file phụ trách chính**:
  - `scripts/seed_data.py`
  - `scripts/backup_restore.bat`
  - `frontend/app.py`
  - `frontend/pages/1_👤_Benh_Nhan.py`
  - `frontend/pages/2_📋_Kham_Benh_Dong.py`
  - `frontend/pages/3_📊_Thong_Ke_Y_Te.py`
  - `docs/backup_restore_guide.md`
  - `docs/demo_script.md`

---

## 📅 3. KẾ HOẠCH TIẾN ĐỘ THEO TUẦN (TIMELINE)

```text
Tuần 1 (Sprint 1): Khởi tạo môi trường, thiết kế Schema CSDL & Pydantic models.
Tuần 2 (Sprint 2): Viết API CRUD nền tảng & Script nạp Dummy Data đạt chuẩn.
Tuần 3 (Sprint 3): Viết 3 Aggregation Pipelines, tối ưu hóa Index & hoàn thiện UI.
Tuần 4 (Sprint 4): Kiểm thử Backup/Restore, đóng gói báo cáo & diễn tập Demo sống.
```

---

## 🎯 4. BẢNG CHECKLIST SẴN SÀNG CHO BUỔI BẢO VỆ

- [x] Đã nạp đủ $\ge 100$ bệnh nhân và $\ge 100$ bệnh án vào MongoDB (`seed_data.py`).
- [x] Đã thiết lập Compound Index `{ department: 1, visit_date: -1 }` và lưu kết quả `explain()`.
- [x] Form nhập bệnh án động hoạt động trơn tru cho 3 chuyên khoa trên Streamlit.
- [x] 3 Aggregation Pipelines hiển thị biểu đồ và cú pháp truy vấn trực quan.
- [x] File backup dữ liệu đã được xuất sẵn dự phòng trong thư mục `./backup/`.
- [x] Cả 3 thành viên nắm vững kịch bản phối hợp trong `docs/demo_script.md`.
