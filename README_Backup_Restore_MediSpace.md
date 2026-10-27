# MEDISPACE — HƯỚNG DẪN BACKUP VÀ RESTORE MONGODB ATLAS

> Tài liệu vận hành cho môi trường Windows của đồ án MediSpace.  
> **Không đưa mật khẩu, file `mongodump.yaml`, dữ liệu BSON bệnh nhân hoặc log chứa thông tin nhạy cảm lên GitHub.**

## 1. Mục đích và phạm vi

- **Backup thủ công:** Sao lưu database chính `medispace_db` bằng `mongodump` khi người vận hành chọn trên menu.
- **Restore thủ công:** Chọn một bản Backup để kiểm tra, Restore sang Atlas TEST, hoặc phục hồi về `medispace_db` chính khi có sự cố và đã dừng ghi dữ liệu.
- **Backup tự động:** Chạy `mongodump` theo lịch Windows Task Scheduler, không tự động Restore.

Các collection cốt lõi hiện tại: `patients` và `medical_records`. Tại lần kiểm thử ngày **27/10/2026**, bản gốc có **10.121** bệnh nhân và **18.186** bệnh án (số lượng thực tế có thể thay đổi). Nhóm đã thử Backup/Restore về Atlas chính và quan sát số `patients` trở lại 10.121; việc đối chiếu đầy đủ còn cần kiểm tra `medical_records`, index và dữ liệu mẫu.

## 2. Cấu trúc thư mục

```text
D:\medispace\
├── scripts\
│   ├── backup_restore.bat          # Menu Backup/Restore thủ công
│   ├── backup_auto.bat             # Chỉ Backup tự động
│   └── README_Backup_Restore_MediSpace.md
├── backup\                      # Các bản Backup BSON
│   ├── 20261027_181133\           # Backup thủ công
│   ├── auto_20261027_184524\      # Backup tự động
│   └── rescue_20261027_181939\    # Backup cứu hộ trước Restore
└── backup_logs\                 # Nhật ký Backup tự động

D:\MongoDBTools\bin\
├── mongodump.exe
└── mongorestore.exe

D:\MediSpaceSecrets\
└── mongodump.yaml                # Bí mật; không commit
```

Các đường dẫn trên là cấu hình đã sử dụng cho MediSpace; nếu triển khai sang máy khác cần cập nhật cho đúng.

## 3. Cấu hình kết nối MongoDB Atlas

| Môi trường | Host | Database | Vai trò |
|---|---|---|---|
| Atlas chính | `cluster0.1rl5eeo.mongodb.net` | `medispace_db` | Nguồn Backup, đích Restore sự cố |
| Atlas TEST | `cluster0.kpdletr.mongodb.net` | `medispace_restore_test` | Kiểm tra khôi phục |

Trong `scripts\backup_restore.bat`, kiểm tra `SOURCE_HOST`, `SOURCE_URI`, `SOURCE_USER`, `SOURCE_DB`, `TEST_HOST`, `TEST_URI`, `TEST_USER`, `TEST_DB`. **Không đổi nhầm chữ `l` thường thành số `1` trong hostname Atlas chính.**

Trên Atlas, cần cấp quyền phù hợp cho tài khoản tương ứng và cho phép kết nối từ địa chỉ IP của máy chạy script. Tài khoản Backup tự động nên là tài khoản riêng có quyền đọc và liệt kê các collection của `medispace_db`, **không có quyền xóa/sửa**. Tài khoản thực hiện Restore cần quyền ghi, tạo collection/index và xóa collection nếu sử dụng chế độ `--drop`.

## 4. Backup thủ công

Mở **CMD**:

```cmd
cd /d D:\medispace
scripts\backup_restore.bat
```

Chọn **1. Backup Atlas chinh** rồi nhập mật khẩu Atlas khi được hỏi. Sau khi có thông báo thành công, ghi nhận tên thư mục được tạo, ví dụ `20261027_181133`.

Chọn **2. Kiem tra file Backup**, nhập tên thư mục vừa tạo. Kết quả phải có:

```text
<ten_thu_muc>\medispace_db\
├── patients.bson
├── patients.metadata.json
├── medical_records.bson
└── medical_records.metadata.json
```

Việc có file và file không rỗng **chỉ là kiểm tra sơ bộ**, chưa chứng minh khôi phục hoàn chỉnh. Nên định kỳ thực hiện Restore thử trên Atlas TEST và kiểm tra kết quả.

## 5. Thiết lập Backup tự động

### 5.1. File script

Script: `D:\medispace\scripts\backup_auto.bat`.

Các biến quan trọng cần kiểm tra trong script:

```bat
set "MONGODUMP=D:\MongoDBTools\bin\mongodump.exe"
set "SOURCE_URI=mongodb+srv://cluster0.1rl5eeo.mongodb.net/"
set "SOURCE_DB=medispace_db"
set "SOURCE_USER=sv3-fe"
set "AUTH_CONFIG=D:\MediSpaceSecrets\mongodump.yaml"
set "BACKUP_ROOT=D:\medispace\backup"
set "LOG_ROOT=D:\medispace\backup_logs"
```

**Lưu ý:** `sv3-fe` là tên tài khoản riêng được đề xuất trong cấu hình script; tài khoản này phải được tạo thật trên Atlas trước khi sử dụng.

Script tạo thư mục `auto_YYYYMMDD_HHMMSS.incomplete` khi đang Backup. Chỉ khi `mongodump` thành công và kiểm tra được các file cốt lõi, script mới đổi thành thư mục `auto_YYYYMMDD_HHMMSS`. Nếu lỗi, thư mục `.incomplete` được giữ lại để điều tra, không được coi là bản Backup hợp lệ.

### 5.2. File mật khẩu cho tác vụ không tương tác

Tạo thư mục `D:\MediSpaceSecrets` và file `mongodump.yaml`:

```yaml
password: 'THAY_BANG_MAT_KHAU_CUA_TAI_KHOAN_BACKUP'
```

**Không sao chép mật khẩu thật vào tài liệu này.** File cấu hình chứa bí mật dạng văn bản: giới hạn quyền NTFS chỉ cho tài khoản chạy Task Scheduler và quản trị viên cần thiết; tránh đưa vào Git, ổ chia sẻ hoặc file ZIP nộp báo cáo. Nếu tài khoản dùng quyền `read` mà công cụ báo thiếu `listCollections`, kiểm tra lại phân quyền trên Atlas.

### 5.3. Chạy thử thủ công

```cmd
cd /d D:\medispace
scripts\backup_auto.bat
echo %errorlevel%
```

- `0`: Script báo Backup thành công.
- `11`: Không tìm thấy file được khai báo tại `AUTH_CONFIG`.
- Khác `0`: Có lỗi; xem `D:\medispace\backup_logs`.

Ví dụ một bản Backup tự động đã tạo trong lần thử của nhóm: `auto_20261027_184524`, đi kèm file `auto_20261027_184524.log`.

Kiểm tra nhanh:

```cmd
dir "D:\medispace\backup" /ad /o-d
dir "D:\medispace\backup_logs" /o-d
type "D:\medispace\backup_logs\auto_20261027_184524.log"
```

Trong log, cần thấy `[SUCCESS] Backup completed.`. Kiểm tra thêm các file BSON và metadata của thư mục mới. Mã `0` và dòng SUCCESS là điều kiện cần, **không thay thế kiểm thử Restore**.

## 6. Đặt lịch chạy qua Windows Task Scheduler

**Chu kỳ được đặt trong Task Scheduler, không phải trong file `backup_auto.bat`.**

1. Nhấn `Win + R`, nhập `taskschd.msc`.
2. Chọn **Create Task**, đặt tên **MediSpace Auto Backup**.
3. **General:** Chọn tài khoản Windows có quyền đọc `mongodump.yaml` và ghi vào thư mục Backup/log. Có thể chọn *Run whether user is logged on or not* nếu cần chạy khi chưa đăng nhập.
4. **Triggers → New:** Chọn *On a schedule* và *Daily*. Đặt thời gian bắt đầu.
5. **Actions → New:** Nhập:

| Trường | Nội dung |
|---|---|
| Program/script | `C:\Windows\System32\cmd.exe` |
| Add arguments | `/c "D:\medispace\scripts\backup_auto.bat"` |
| Start in | `D:\medispace` |

6. **Settings:** *If the task is already running → Do not start a new instance*. Có thể chọn *Run task as soon as possible after a scheduled start is missed*.
7. Lưu tác vụ. Nhấp chuột phải tác vụ → **Run** để thử ngay, kiểm tra **Last Run Result** và file log.

### 6.1. Cấu hình thử nghiệm: mỗi 5 phút

Trong **Triggers → Edit → Advanced settings**:

- *Repeat task every*: **5 minutes**.
- *For a duration of*: **1 day**.
- Bật **Enabled**.

Lặp lại qua các ngày phụ thuộc cấu hình trigger và Windows; kiểm tra **Next Run Time** để xác nhận lịch thực tế. Sau khi quan sát ít nhất hai bản Backup mới cách nhau khoảng 5 phút, cần **đổi lịch sang chu kỳ vận hành**, tránh đầy ổ cứng.

### 6.2. Cấu hình vận hành đề xuất

- **Mỗi 6 giờ:** Trigger lặp lại mỗi **6 hours**, thời lượng **1 day**.
- **Mỗi ngày lúc 02:00:** Trigger Daily, giờ bắt đầu **02:00**, không cần lặp lại trong ngày.

Các lựa chọn này là ví dụ cho đồ án, không phải cam kết đáp ứng yêu cầu phục hồi của môi trường y tế thực tế. Windows Task Scheduler cần máy đang hoạt động hoặc hỗ trợ chạy bù khi máy hoạt động trở lại; cũng cần kết nối mạng và truy cập Atlas.

## 7. Kiểm tra Backup tự động theo lịch

Dùng CMD:

```cmd
dir "D:\medispace\backup" /ad /o-d
dir "D:\medispace\backup_logs" /o-d
```

Trong Task Scheduler, kiểm tra:

- **Last Run Time**: thời điểm lần chạy gần nhất.
- **Last Run Result = 0x0**: Task báo kết thúc thành công.
- **Next Run Time**: lịch tiếp theo.
- Log tương ứng có dòng **SUCCESS** và file BSON/metadata tồn tại.

**Lưu ý:** Chỉ thấy một thư mục `auto_...` chưa đủ xác nhận lịch lặp 5 phút hoạt động; phải quan sát ít nhất lần chạy tiếp theo mà không thao tác thủ công.

## 8. Restore — kiểm thử và xử lý sự cố

### 8.1. Restore thử trên Atlas TEST

Với script menu hiện có:

- Mục 3: Dry Run Restore vào Atlas TEST.
- Mục 4: Restore thật vào Atlas TEST.

Dry Run không ghi document. Nếu TEST đã có dữ liệu, Restore lặp lại mà không `--drop` có thể gặp lỗi trùng `_id`. Cần kiểm tra trạng thái database đích và log, không chạy lặp lại tùy tiện.

### 8.2. Restore về Atlas chính

Menu mục 5 (nếu đã ghép phần `:RESTORE_MAIN`) dùng để phục hồi về **`medispace_db` đang được ứng dụng sử dụng**. Quy trình:

1. Xác định chính xác bản Backup cần phục hồi.
2. Kiểm tra file và chạy Dry Run.
3. **Dừng các thao tác ghi vào database từ FastAPI và mọi nguồn khác.**
4. Tạo bản Backup cứu hộ trạng thái hiện tại và kiểm tra kết quả.
5. Hiểu rõ `mongorestore --drop` sẽ xóa collection đích trước khi nạp lại. Đây **không phải** thao tác có thể tự hoàn tác, và dữ liệu mới hơn bản Backup có thể bị mất.
6. Chỉ xác nhận Restore thật khi đã chấp nhận rủi ro và có kế hoạch xử lý nếu giữa chừng thất bại.
7. Sau Restore, kiểm tra document, index và API; chỉ mở lại thao tác ghi khi đã xác nhận đầy đủ.

**Không cấu hình tự động Restore lên Atlas chính.** `backup_auto.bat` chỉ được phép Backup.

Lưu ý: Đoạn Restore đang nhắm tới hai collection `patients` và `medical_records`, không nhất thiết phục hồi mọi collection khác nếu sau này dự án bổ sung bảng dữ liệu mới. Cần điều chỉnh phạm vi cùng kế hoạch phục hồi nếu cấu trúc dự án thay đổi.

### 8.3. Kiểm tra MongoDB Compass sau Restore

Kết nối đúng cluster và chạy Mongosh:

```javascript
const m = db.getSiblingDB("medispace_db");
print("Patients:", m.patients.countDocuments({}));
print("Medical records:", m.medical_records.countDocuments({}));
printjson(m.patients.getIndexes());
printjson(m.medical_records.getIndexes());
```

Đối chiếu số lượng với **thời điểm của bản Backup được chọn**, kiểm tra thêm hồ sơ mẫu và API. Chỉ số đếm khớp chưa đảm bảo toàn bộ dữ liệu và quan hệ nghiệp vụ nhất quán.


## 9. Các lỗi thường gặp

| Hiện tượng | Nguyên nhân / cách xử lý |
|---|---|
| `errorlevel = 11` | Thiếu `D:\MediSpaceSecrets\mongodump.yaml` hoặc sai `AUTH_CONFIG`. |
| DNS lookup fail | Kiểm tra hostname Atlas, kết nối Internet và DNS; đặc biệt phân biệt `l` và `1`. |
| `listCollections` không được cấp quyền | Xem lại quyền tài khoản Database Access trong Atlas. |
| `duplicate key` khi Restore | Database/collection đích đã có document cùng `_id`; kiểm tra chế độ Restore, không tự ý thêm `--drop` vào database chính. |
| Task Scheduler `0x0` nhưng không thấy bản mới | Đối chiếu thời gian chạy, tài khoản Windows, log và `BACKUP_ROOT`. |
| Không chạy đúng giờ | Kiểm tra Trigger, Next Run Time, nguồn điện, trạng thái máy, mạng và tùy chọn chạy bù. |
| Thư mục `.incomplete` | Backup chưa hoàn tất hoặc kiểm tra file thất bại; xem log, không dùng bản này để Restore. |
| Backup tự động không hiện trong menu Restore | `CHECK_BACKUP` có thể mới nhận mẫu `YYYYMMDD_HHMMSS`, chưa nhận `auto_YYYYMMDD_HHMMSS`; cần cập nhật hàm kiểm tra trước khi dùng. |

## 10. An toàn dữ liệu và phân quyền

- Không lưu mật khẩu trong code, log, README hoặc GitHub.
- Phân quyền Backup (chỉ đọc) tách khỏi quyền Restore (ghi/xóa).
- Bảo vệ thư mục chứa BSON vì có thể chứa thông tin bệnh nhân nhạy cảm.
- Giữ các bản Backup cứu hộ trước Restore; tránh tự động xóa bản Backup cũ khi chưa có chính sách lưu giữ và kiểm chứng.
- Với môi trường chạy thực tế, bổ sung sao lưu bên ngoài máy cá nhân, mã hóa dữ liệu lưu và kiểm thử phục hồi định kỳ.
- Nếu mật khẩu tài khoản Atlas từng bị dán lên chat, màn hình công khai hoặc commit, cần thay đổi mật khẩu đó.
