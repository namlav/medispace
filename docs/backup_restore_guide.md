# HƯỚNG DẪN QUY TRÌNH BACKUP & RESTORE CSDL MONGODB
**Phục vụ nội dung đánh giá: Kiểm thử hiệu năng & Demo trực quan (Barem SV3)**

---

## 1. Phương Pháp 1: Thực Hiện Trực Tiếp Trên GUI Tool (MongoDB Compass)

Đây là thao tác chính mà **SV3** sẽ thực hiện trực tiếp trước mặt hội đồng trong kịch bản bảo vệ.

### 1.1. Quy trình Export / Backup Dữ liệu trên Compass
1. Mở **MongoDB Compass** và kết nối vào CSDL `medispace_db`.
2. Chọn collection `medical_records`.
3. Bấm vào menu **Collection** ở thanh trên cùng $\rightarrow$ Chọn **Export Collection**.
4. Chọn tùy chọn: **Export full collection** $\rightarrow$ Bấm **Select Fields** (giữ nguyên toàn bộ các trường).
5. Chọn định dạng: **JSON** $\rightarrow$ Chọn đường dẫn lưu file (ví dụ: `E:\nosql_subj\medispace\backup\medical_records.json`).
6. Bấm **Export** $\rightarrow$ Chờ thông báo thành công (ví dụ: *150 documents exported*).

### 1.2. Thao tác mô phỏng sự cố & Restore trên Compass
1. **Mô phỏng sự cố mất dữ liệu**:
   - Trên Compass, vào collection `medical_records`, chọn tab **Documents**.
   - Bấm nút **Drop Collection** (hoặc xóa một vài document điển hình) để chứng minh dữ liệu bị mất.
2. **Tiến hành Phục hồi (Restore)**:
   - Tạo lại collection `medical_records` (nếu vừa xóa cả collection).
   - Bấm vào nút **Add Data** $\rightarrow$ Chọn **Import JSON or CSV File**.
   - Trỏ tới file vừa export: `medical_records.json`.
   - Chọn định dạng **JSON** và nhấn **Import**.
   - Compass sẽ nạp lại toàn bộ dữ liệu và hiển thị nguyên vẹn các trường động ban đầu.

---

## 2. Phương Pháp 2: Thực Hiện Qua Dòng Lệnh (CLI Tools)

### 2.1. Lệnh Sao Lưu (Backup Toàn Bộ Database)
```bash
mongodump --db medispace_db --out ./backup/
```
*Kết quả:* Tạo ra thư mục `./backup/medispace_db/` chứa các file `patients.bson`, `patients.metadata.json`, `medical_records.bson`, `medical_records.metadata.json`.

### 2.2. Lệnh Phục Hồi (Restore Database)
```bash
mongorestore --db medispace_db --drop ./backup/medispace_db/
```
*Ghi chú:* Tham số `--drop` đảm bảo xóa sạch dữ liệu cũ trong CSDL trước khi nạp lại để tránh trùng lặp khóa chính `_id`.
