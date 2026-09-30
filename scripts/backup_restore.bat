@echo off
chcp 65001 > nul
echo ========================================================
echo   MEDISPACE - MONGODB BACKUP & RESTORE TOOL
echo ========================================================
echo 1. Backup to folder ./backup/
echo 2. Restore from folder ./backup/
echo 3. Exit
echo.
set /p choice="Nhập lựa chọn (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo [*] Đang thực hiện sao lưu CSDL 'medispace_db'...
    mongodump --db medispace_db --out ./backup/
    if %errorlevel% neq 0 (
        echo [!] Lỗi khi sao lưu. Đảm bảo 'mongodump' đã được cài đặt và thêm vào PATH.
    ) else (
        echo [✓] Sao lưu thành công vào thư mục ./backup/medispace_db/
    )
    pause
    exit /b
)

if "%choice%"=="2" (
    echo.
    echo [!] CẢNH BÁO: Thao tác này sẽ phục hồi dữ liệu từ thư mục ./backup/medispace_db/
    set /p confirm="Bạn có chắc chắn muốn tiếp tục? (y/n): "
    if /i "%confirm%"=="y" (
        mongorestore --db medispace_db --drop ./backup/medispace_db/
        if %errorlevel% neq 0 (
            echo [!] Lỗi khi phục hồi. Đảm bảo 'mongorestore' đã được cài đặt.
        ) else (
            echo [✓] Phục hồi CSDL thành công!
        )
    )
    pause
    exit /b
)

echo Đã thoát.
