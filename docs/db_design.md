# BÁO CÁO THIẾT KẾ CƠ SỞ DỮ LIỆU NOSQL (MONGODB)
**Hệ Thống Quản Lý Hồ Sơ Bệnh Án Điện Tử Tại Phòng Khám Đa Khoa**

---

## 1. Giải Trình Sự Cần Thiết Của CSDL Document Đối Với Dữ Liệu Y Tế (1.0 Điểm)

### 1.1. Bản chất không đồng nhất của dữ liệu khám bệnh chuyên khoa
Trong một phòng khám đa khoa hiện đại, quy trình tiếp đón hành chính của các bệnh nhân là tương tự nhau (họ tên, ngày sinh, số điện thoại, địa chỉ, nhóm máu). Tuy nhiên, khi bệnh nhân bước vào các phòng khám chuyên khoa khác nhau, các tham số lâm sàng cần thu thập hoàn toàn tách biệt:
* **Khoa Tim Mạch**: Cần theo dõi chỉ số huyết áp (tâm thu/tâm trương), nhịp tim mỗi phút, kết quả điện tâm đồ (ECG), phân suất tống máu cơ tim ($EF\%$), phân tầng nguy cơ tim mạch.
* **Khoa Da Liễu**: Cần ghi nhận vị trí sang thương (mặt, cánh tay, lưng...), loại tổn thương (dạng dát đỏ, sẩn, mụn nước, mụn mủ), mức độ ngứa rát, xét nghiệm dị nguyên áp bì (patch test), yếu tố lây nhiễm.
* **Khoa Răng - Hàm - Mặt**: Cần ghi nhận sơ đồ 32 chiếc răng (dental chart), tình trạng từng răng cụ thể (sâu men, viêm tủy, răng khôn mọc lệch), độ vôi răng (Grade 1-3), tình trạng nha chu và viêm nướu.

### 1.2. Hạn chế của CSDL Quan Hệ (RDBMS)
Nếu cố gắng áp dụng mô hình quan hệ (Relational Model) truyền thống vào bài toán này, kiến trúc dữ liệu sẽ gặp phải 3 bế tắc lớn:
1. **Mô hình EAV (Entity-Attribute-Value)**: Phải tạo bảng lưu thuộc tính động dạng `(record_id, attribute_name, attribute_value)`. Cách này làm mất hoàn toàn tính toàn vẹn kiểu dữ liệu (data types), khiến việc truy vấn, lọc hay tính toán thống kê trở nên chậm chạp và phức tạp.
2. **Bùng nổ số lượng bảng (Table Explosion)**: Mỗi khi mở thêm một chuyên khoa mới (ví dụ: Mắt, Tai Mũi Họng), lập trình viên và DBA phải thực hiện migration, tạo thêm bảng mới và viết lại hàng loạt câu lệnh `JOIN`.
3. **Hiện tượng bảng thưa thớt (Sparse Columns & NULLs)**: Nếu gộp tất cả trường của mọi chuyên khoa vào một bảng `MedicalRecords`, bảng sẽ có hàng chục đến hàng trăm cột nhưng mỗi bản ghi chỉ dùng khoảng 5-10% số cột, 90% còn lại mang giá trị `NULL`, gây lãng phí bộ nhớ lưu trữ và chỉ mục.

### 1.3. Giải pháp tối ưu: Document-based Model (MongoDB)
* **Schema-less / Polymorphic Pattern**: MongoDB cho phép các Document trong cùng một collection có cấu trúc trường khác nhau. Điều này cho phép lưu trữ hồ sơ của tất cả các chuyên khoa trong duy nhất collection `medical_records`.
* **Khả năng mở rộng không giới hạn**: Khi phòng khám mở thêm chuyên khoa Thần Kinh hay Nhãn Khoa, hệ thống chỉ việc lưu thêm các trường tương ứng vào sub-document `specialty_data` mà **không cần sửa đổi cấu trúc CSDL (zero-downtime schema evolution)**.

---

## 2. Thiết Kế Cấu Trúc Document Bệnh Án Linh Hoạt & Đơn Thuốc (1.5 Điểm)

### 2.1. Quyết định kiến trúc: Embedded vs Referenced
* **Collection `patients` (Referenced)**: Chứa thông tin bệnh nhân. Tách riêng khỏi lượt khám để tránh vi phạm *Unbounded Array Anti-pattern* (khi bệnh nhân khám bệnh suốt đời, mảng lượt khám có thể vượt quá giới hạn 16MB của một Document MongoDB).
* **Collection `medical_records` (Embedded Prescriptions & Polymorphic Specialty Data)**:
  - Trường `patient_id`: Khóa ngoại tham chiếu đến `patients._id`.
  - Mảng `prescriptions`: Thiết kế dạng **Embedded Document Array** lồng trực tiếp trong phiếu khám vì đơn thuốc luôn gắn liền với buổi khám đó và số lượng thuốc thường chỉ từ 2 đến 10 loại thuốc.
  - Trường `specialty_data`: Chứa Object động chứa dữ liệu riêng biệt của từng chuyên khoa.

---

## 3. Lược Đồ Chi Tiết (Schema Specifications)

### 3.1. Collection `patients`
```json
{
  "_id": ObjectId("665a1b2c3d4e5f6a7b8c9d01"),
  "patient_code": "BN-0001",
  "full_name": "Nguyễn Văn Hùng",
  "dob": "1978-05-12",
  "gender": "Nam",
  "phone": "0912345678",
  "address": "Số 45, Đường Giải Phóng, Hà Nội",
  "blood_group": "O+",
  "allergies": ["Dị ứng Penicillin"],
  "created_at": ISODate("2026-01-10T08:00:00Z")
}
```

### 3.2. Collection `medical_records` (Mẫu chuyên khoa Tim Mạch)
```json
{
  "_id": ObjectId("665a2c3d4e5f6a7b8c9d0102"),
  "patient_id": "665a1b2c3d4e5f6a7b8c9d01",
  "record_code": "BA-2026-0001",
  "department": "TIM_MACH",
  "doctor_name": "BS. CKII Nguyễn Văn Hùng",
  "visit_date": ISODate("2026-09-15T08:30:00Z"),
  "symptoms": "Hồi hộp, tức ngực trái khi gắng sức",
  "diagnosis": "Tăng huyết áp vô căn độ 2",
  "specialty_data": {
    "blood_pressure": { "systolic": 155, "diastolic": 95 },
    "heart_rate_bpm": 86,
    "ecg_result": "ST chênh xuống 1mm ở chuyển đạo V4-V6",
    "ejection_fraction_ef": 56,
    "cardiovascular_risk": "Cao"
  },
  "prescriptions": [
    { "medicine_name": "Amlodipine", "dosage": "5mg", "quantity": 30, "usage": "Uống 1 viên vào 8h sáng" },
    { "medicine_name": "Atorvastatin", "dosage": "20mg", "quantity": 30, "usage": "Uống 1 viên vào 20h tối" }
  ],
  "follow_up_required": true,
  "follow_up_date": ISODate("2026-10-15T08:30:00Z"),
  "created_at": ISODate("2026-09-15T08:30:00Z")
}
```
