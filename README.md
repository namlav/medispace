# MediSpace - Hệ Thống Quản Lý Hồ Sơ Bệnh Án Điện Tử (NoSQL - MongoDB)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0%2B-brightgreen.svg)](https://www.mongodb.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red.svg)](https://streamlit.io/)

Đồ án môn học: **Cơ Sở Dữ Liệu NoSQL**  
Chủ đề: **Quản lý hồ sơ bệnh án điện tử tại phòng khám đa khoa**  
Hệ quản trị CSDL chính: **MongoDB**  
Quy mô nhóm: **03 Sinh viên**  

---

## 📑 Tài Liệu Trọng Tâm Dành Cho Nhóm & Giảng Viên
* 📋 **[BẢNG PHÂN CÔNG NHIỆM VỤ & THEO DÕI TIẾN ĐỘ](PHAN_CONG_NHIEM_VU.md)** (Chi tiết công việc và barem điểm từng sinh viên)
* 📐 **[Báo cáo thiết kế CSDL Document & Giải trình NoSQL](docs/db_design.md)** (Phục vụ 2.5đ Thiết kế CSDL)
* ⚡ **[Tài liệu giải thích Aggregation Pipelines & Tối ưu Index](docs/aggregation_explained.md)** (Phục vụ 2.5đ Chức năng nâng cao)
* 💾 **[Hướng dẫn Backup & Restore trên MongoDB Compass GUI](docs/backup_restore_guide.md)** (Phục vụ 1.5đ Kiểm thử & Demo)
* 🎬 **[Kịch bản phối hợp Demo sống 4 bước bảo vệ](docs/demo_script.md)** (Kịch bản phân vai 3 sinh viên khi thuyết trình)

---

## 📌 1. Giới Thiệu Đề Tài
Hệ thống quản lý hồ sơ bệnh nhân, hỗ trợ ghi nhận bệnh án linh hoạt theo từng chuyên khoa (**Tim Mạch**, **Da Liễu**, **Răng - Hàm - Mặt**) và theo dõi lịch sử điều trị/đơn thuốc dựa trên mô hình **Document Schema-less** của MongoDB.

### Các điểm nhấn kỹ thuật theo barem đánh giá:
1. **Schema-less / Polymorphic Document Pattern (Báo cáo & Thiết kế CSDL - 2.5đ)**:
   - Lưu trữ các mẫu bệnh án chuyên khoa với thuộc tính lâm sàng hoàn toàn khác biệt trong cùng collection `medical_records`.
   - Nhúng trực tiếp mảng đơn thuốc (`prescriptions`) dạng **Embedded Document Array** giúp truy vấn hồ sơ khám nhanh chóng chỉ trong 1 thao tác đọc (`single read`).
2. **Chức năng CRUD Nền tảng (2.5đ)**:
   - Thêm mới bệnh nhân, lập phiếu khám bệnh, kê đơn thuốc và quản lý lịch sử khám.
3. **Chức năng nâng cao đặc trưng (2.5đ)**:
   - Pipeline 1: Thống kê số lượng ca bệnh và số ca tái khám theo từng chuyên khoa.
   - Pipeline 2: Phân tích phân bố ca bệnh theo nhóm độ tuổi (`$lookup`, `$unwind`, `$switch`).
   - Pipeline 3: Tính toán tần suất và tỷ lệ tái khám của bệnh nhân (`$facet`, `$bucket`).
   - Tối ưu hóa truy vấn với Compound Index `{ department: 1, visit_date: -1 }` (chứng minh qua `explain("executionStats")`).
4. **Kiểm thử hiệu năng & Demo trực quan (2.5đ)**:
   - **Dummy Data**: Script sinh tự động $\ge 120$ hồ sơ bệnh nhân và $\ge 150$ lượt khám bệnh phân bổ 3 chuyên khoa.
   - **Demo sống**: Form nhập bệnh án động (Streamlit) + MongoDB Compass + Quy trình Backup/Restore.

---

## 👥 2. Tóm Tắt Phân Công Trách Nhiệm & Nhánh Git

| Thành viên | Vai trò phụ trách | Trọng tâm công việc | Nhánh đề xuất (Git) |
| :--- | :--- | :--- | :--- |
| **SV1** | **Data Architect & CRUD Lead** | Thiết kế Document schema đa chuyên khoa, lập trình API CRUD Bệnh nhân & Bệnh án, thao tác nhập bệnh án demo | `feat/sv1-db-models`<br>`feat/sv1-patient-crud`<br>`feat/sv1-record-crud` |
| **SV2** | **Advanced Query Specialist** | Xây dựng 3 Aggregation Pipelines (Khoa, Độ tuổi, Tái khám), tối ưu hóa Index & đo đạc `executionStats` | `feat/sv2-dept-stats`<br>`feat/sv2-age-revisit`<br>`feat/sv2-indexes` |
| **SV3** | **Fullstack Integrator & DB Tester** | Script nạp 100+ Dummy Data, thiết kế Form nhập bệnh án động (Streamlit), thực hiện Backup/Restore trên GUI và điều phối Demo | `feat/sv3-dummy-data`<br>`feat/sv3-dynamic-ui`<br>`docs/sv3-demo-backup` |

*(Chi tiết xem tại: [PHAN_CONG_NHIEM_VU.md](PHAN_CONG_NHIEM_VU.md))*

---

## 📂 3. Cấu Trúc Thư Mục Dự Án
```text
medispace/
├── backend/
│   ├── app/
│   │   ├── core/           # Cấu hình env & kết nối MongoClient
│   │   ├── models/         # Pydantic Schemas (Patient, MedicalRecord)
│   │   ├── services/       # CRUD logic & Aggregation service
│   │   ├── api/v1/         # Endpoints RESTful API (/patients, /records, /analytics)
│   │   └── main.py         # Entrypoint FastAPI & CORS
│   └── requirements.txt
├── frontend/
│   ├── app.py              # Dashboard Streamlit chính
│   └── pages/
│       ├── 1_👤_Benh_Nhan.py       # Quản lý danh sách & tạo bệnh nhân
│       ├── 2_📋_Kham_Benh_Dong.py  # Form khám bệnh động theo chuyên khoa
│       └── 3_📊_Thong_Ke_Y_Te.py   # Dashboard biểu đồ thống kê từ Aggregation
├── scripts/
│   ├── seed_data.py        # Sinh >= 100 BN và >= 150 bệnh án mẫu
│   ├── create_indexes.py   # Thiết lập Index & đo lường executionStats
│   └── backup_restore.bat  # Script sao lưu/phục hồi bằng mongodump/mongorestore
├── docs/
│   ├── db_design.md        # Giải trình CSDL Document & Lược đồ
│   ├── aggregation_explained.md # Giải thích chi tiết các pipeline Aggregation
│   ├── backup_restore_guide.md  # Hướng dẫn Backup/Restore trên GUI Compass
│   └── demo_script.md      # Kịch bản demo sống phân vai 3 thành viên
├── PHAN_CONG_NHIEM_VU.md   # Phân chia chi tiết nhiệm vụ và theo dõi tiến độ
├── .env.example
├── .gitignore
├── config.md               # Đề bài & barem điểm môn học
└── README.md
```

---

## 🚀 4. Hướng Dẫn Cài Đặt & Chạy Thử

### Bước 1: Chuẩn bị môi trường Python
```bash
# Kích hoạt venv (nếu có) và cài đặt dependencies
pip install -r requirements.txt
```

### Bước 2: Cấu hình biến môi trường
Tạo file `.env` từ `.env.example`:
```ini
MONGO_URI=mongodb://localhost:27017
DB_NAME=medispace_db
```
*(Nếu sử dụng MongoDB Atlas Cloud, thay `MONGO_URI` bằng chuỗi kết nối từ Atlas)*

### Bước 3: Nạp dữ liệu mẫu đạt chuẩn định mức (Dummy Data)
```bash
python scripts/seed_data.py
```
*Kết quả:* Nạp thành công $\ge 120$ bệnh nhân và $\ge 150$ bệnh án phân bổ vào 3 chuyên khoa.

### Bước 4: Tạo và tối ưu Index
```bash
python scripts/create_indexes.py
```
*Kết quả:* Tạo Compound Index và hiển thị so sánh hiệu năng truy vấn `executionStats`.

### Bước 5: Khởi chạy ứng dụng

* **Khởi động Giao diện Web (Streamlit UI)**:
```bash
streamlit run frontend/app.py
```
Truy cập giao diện tại: `http://localhost:8501`

* **Khởi động Backend RESTful API (FastAPI)**:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Truy cập Swagger UI tài liệu API tại: `http://localhost:8000/docs`
