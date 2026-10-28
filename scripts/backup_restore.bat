@echo off
setlocal DisableDelayedExpansion
chcp 65001 >nul

title Medispace - Backup Restore Test

REM=============================
REM 1. Duong Dan cong cu
REM==============================

set "MONGODUMP=E:\mongodb-database-tools-windows-x86_64-100.18.0\bin\mongodump.exe"
set "MONGORESTORE=E:\mongodb-database-tools-windows-x86_64-100.18.0\bin\mongorestore.exe"


REM===========================
REM 2. ATLAS Nguon backup
REM===============================

set "SOURCE_HOST=cluster0.1rl5eeo.mongodb.net"
set "SOURCE_URI=mongodb+srv://cluster0.1rl5eeo.mongodb.net/"
set "SOURCE_USER=sv3-fe"
set "SOURCE_DB=medispace_db"

REM===============================
REM 3. ATLAS TEST - CHI RESTORE
REM ======================================

set "TEST_HOST=cluster0.kpdletr.mongodb.net"
set "TEST_URI=mongodb+srv://cluster0.kpdletr.mongodb.net/"
set "TEST_USER=user1"
set "TEST_DB=medispace_restore_test"

REM ======================================
REM 4. THU MUC SAO LUUE:\nosql_subj\medispace
REM ======================================

set "BACKUP_ROOT=E:\nosql_subj\medispace\backup"


REM ======================================
REM 5. KIEM TRA CONG CU
REM ======================================

if not exist "%MONGODUMP%" (
    echo [LOI] khong tin thay mongodump.exe
    pause
    exit /b 1
)
if not exist "%MONGORESTORE%" (
    echo [Loi] ko tim thay mongorestore.exe
    pause
    exit /b 1
)

REM Khong cho 2 cluster trung hostname
if /I "%SOURCE_HOST%" == "%TEST_HOST%" (
    echo [Loi] cluster nguon va dich trung nhhau
    pause
    exit /b 1
)

REM Database nguon va dich phai khac ten

if /I "%SOURCE_DB%" == "%TEST_DB%" (
    echo [Loi] database nguon va dich trung ten
    pause
    exit /b 1
)

if not exist "%BACKUP_ROOT%" (
    mkdir "%BACKUP_ROOT%"
)

REM ======================================
REM 6. MENU CHINH
REM ======================================

:MENU
cls
echo ============================================
echo       MEDISPACE BACKUP RESTORE
echo ============================================
echo.
echo SOURCE : MongoDB Atlas CHINH
echo DB     : %SOURCE_DB%
echo.
echo TARGET : MongoDB Atlas TEST
echo DB     : %TEST_DB%
echo.
echo 1. Backup Atlas chinh
echo 2. Kiem tra file Backup
echo 3. Dry Run Restore vao Atlas TEST
echo 4. Restore that vao Atlas TEST
echo 5. Restore vao Atlas CHINH
echo 6. Thoat
echo.

set "CHOICE="
set /p "CHOICE=Chon (1-5): "

if "%CHOICE%"=="1" goto BACKUP
if "%CHOICE%"=="2" goto VERIFY
if "%CHOICE%"=="3" goto DRY_RUN
if "%CHOICE%"=="4" goto RESTORE_TEST
if "%CHOICE%"=="5" goto RESTORE_MAIN
if "%CHOICE%"=="6" goto END

echo Lua chon khong hop le.
pause
goto MENU

REM ======================================
REM 7. BACKUP ATLAS CHINH
REM ======================================

:BACKUP
cls

echo ============================================
echo BACKUP DATABASE TU ATLAS CHINH
echo ============================================
echo.
echo Database: %SOURCE_DB%
echo Host: %SOURCE_HOST%
echo.

REM Tao timestamp cho thu muc Backup
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%i"

REM Gan dung ten bien BACKUP_DIR
set "BACKUP_DIR=%BACKUP_ROOT%\%STAMP%"

REM Tao thu muc neu chua ton tai
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Kiem tra tao thu muc thanh cong
if not exist "%BACKUP_DIR%\" (
    echo [LOI] Khong tao duoc thu muc Backup.
    pause
    goto MENU
)

echo Thu muc Backup:
echo %BACKUP_DIR%
echo.
echo Chi doc du lieu Atlas, khong xoa document.
echo.

REM Backup vao thu muc tren may
REM Nhap password khi mongodump yeu cau
"%MONGODUMP%" --uri="%SOURCE_URI%" --username="%SOURCE_USER%" --authenticationDatabase=admin --db="%SOURCE_DB%" --out="%BACKUP_DIR%"

if errorlevel 1 (
    echo.
    echo [LOI] Backup that bai.
    pause
    goto MENU
)

REM Kiem tra file benh nhan
if not exist "%BACKUP_DIR%\%SOURCE_DB%\patients.bson" (
    echo [LOI] Khong tim thay patients.bson.
    pause
    goto MENU
)

REM Kiem tra file benh an
if not exist "%BACKUP_DIR%\%SOURCE_DB%\medical_records.bson" (
    echo [LOI] Khong tim thay medical_records.bson.
    pause
    goto MENU
)

echo.
echo [THANH CONG] Backup hoan tat.
echo Thu muc: %BACKUP_DIR%
echo.
pause
goto MENU


REM ======================================
REM 8. KIEM TRA FILE BACKUP
REM ======================================

:VERIFY
cls
echo ==============Kiem tra file back up =============
echo.

dir "%BACKUP_ROOT%" /ad

echo. 
set "STAMP="
set /p "STAMP= nhap ten thu muc BACK up"

call :CHECK_BACKUP

if errorlevel 1 (
    pause
    goto MENU
)

echo.
echo Danh sach file:
dir "%BACKUP_DIR%\%SOURCE_DB%"
echo.
echo [OK] Da tim thay hai file BSON.
echo Chua xac nhan kha nang Restore.
echo.
pause
goto MENU


REM ======================================
REM 9. HAM KIEM TRA BAN BACKUP
REM ======================================

:CHECK_BACKUP

REM Kiem tra ten theo dang YYYYMMDD_HHMMSS
echo(%STAMP%| findstr /R "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]$" >nul

if errorlevel 1 (
    echo [LOI] Ten thu muc Backup khong hop le.
    exit /b 1
)

set "BACKUP_DIR=%BACKUP_ROOT%\%STAMP%"

if not exist "%BACKUP_DIR%\%SOURCE_DB%\patients.bson" (
    echo [LOI] Khong tim thay patients.bson.
    exit /b 1
)

if not exist "%BACKUP_DIR%\%SOURCE_DB%\medical_records.bson" (
    echo [LOI] Khong tim thay medical_records.bson.
    exit /b 1
)

for %%F in ("%BACKUP_DIR%\%SOURCE_DB%\patients.bson") do (
    if %%~zF EQU 0 (
        echo [LOI] File patients.bson rong.
        exit /b 1
    )
)

for %%F in ("%BACKUP_DIR%\%SOURCE_DB%\medical_records.bson") do (
    if %%~zF EQU 0 (
        echo [LOI] File medical_records.bson rong.
        exit /b 1
    )
)

exit /b 0

REM ======================================
REM 10. DRY RUN RESTORE
REM ======================================

:DRY_RUN
cls

echo ===== DRY RUN RESTORE =====
echo.
echo Chi kiem tra, KHONG nap document.
echo.

dir "%BACKUP_ROOT%" /ad

echo.
set "STAMP="
set /p "STAMP=Nhap ten thu muc Backup: "

call :CHECK_BACKUP

if errorlevel 1 (
    pause
    goto MENU
)

echo.
echo Atlas TEST: %TEST_HOST%
echo Database dich: %TEST_DB%
echo.
if /I not "%TEST_HOST%"=="cluster0.kpdletr.mongodb.net" (
    echo [LOI] Sai hostname Atlas TEST.
    pause
    goto MENU
)

if /I not "%TEST_DB%"=="medispace_restore_test" (
    echo [LOI] Sai database TEST.
    pause
    goto MENU


"%MONGORESTORE%" ^
 --uri="%TEST_URI%" ^
 --username="%TEST_USER%" ^
 --authenticationDatabase=admin ^
 --password="" ^
 --nsInclude="%SOURCE_DB%.patients" ^
 --nsInclude="%SOURCE_DB%.medical_records" ^
 --nsFrom="%SOURCE_DB%.*" ^
 --nsTo="%TEST_DB%.*" ^
 --dryRun ^
 --verbose ^
 --dir="%BACKUP_DIR%"

if errorlevel 1 (
    echo.
    echo [LOI] Dry Run that bai.
    pause
    goto MENU
)

echo.
echo [OK] Dry Run hoan tat.
echo Chua co document nao duoc Restore.
echo.
pause
goto MENU

REM ======================================
REM 11. RESTORE THAT VAO ATLAS TEST
REM ======================================

:RESTORE_TEST
cls

echo ============================================
echo      RESTORE VAO ATLAS TEST
echo ============================================
echo.
echo KHONG RESTORE VAO ATLAS CHINH.
echo.
echo Host dich: %TEST_HOST%
echo Database dich: %TEST_DB%
echo.

REM Kiem tra dung Atlas TEST du kien

if /I not "%TEST_URI%"=="mongodb+srv://cluster0.kpdletr.mongodb.net/" (
    echo [LOI] URI Restore khong dung Atlas TEST.
    pause
    goto MENU
)

REM Kiem tra database dich

if /I not "%TEST_DB%"=="medispace_restore_test" (
    echo [LOI] Sai database dich.
    pause
    goto MENU
)

REM Chon ban Backup

dir "%BACKUP_ROOT%" /ad

echo.
set "STAMP="
set /p "STAMP=Nhap ten thu muc Backup: "

call :CHECK_BACKUP

if errorlevel 1 (
    pause
    goto MENU
)

echo.
echo ============================================
echo CANH BAO: SAP GHI DU LIEU LEN ATLAS TEST
echo ============================================
echo.
echo Cluster: %TEST_HOST%
echo Database: %TEST_DB%
echo.
echo KHONG su dung --drop.
echo Nen su dung database TEST rong.
echo.

set "CONFIRM="
set /p "CONFIRM=Nhap RESTORE-TEST de xac nhan: "

if /I not "%CONFIRM%"=="RESTORE-TEST" (
    echo Da huy Restore.
    pause
    goto MENU
)

echo.
echo Dang Restore vao Atlas TEST...
echo.

"%MONGORESTORE%" ^
 --uri="%TEST_URI%" ^
 --username="%TEST_USER%" ^
 --authenticationDatabase=admin ^
 --password="" ^
 --nsInclude="%SOURCE_DB%.patients" ^
 --nsInclude="%SOURCE_DB%.medical_records" ^
 --nsFrom="%SOURCE_DB%.*" ^
 --nsTo="%TEST_DB%.*" ^
 --stopOnError ^
 --dir="%BACKUP_DIR%"

if errorlevel 1 (
    echo.
    echo [LOI] Restore gap loi.
    echo Kiem tra log va du lieu TEST.
    pause
    goto MENU
)

echo.
echo [THANH CONG] Restore da hoan tat.
echo.
echo Cluster TEST: %TEST_HOST%
echo Database: %TEST_DB%
echo.
echo Hay doi chieu so documents tren Compass.
echo.
pause
goto MENU



REM ======================================
REM 12. RESTORE VAO ATLAS CHINH
REM ======================================

:RESTORE_MAIN
cls

echo ============================================
echo    RESTORE DATABASE ATLAS CHINH
echo ============================================
echo.
echo Host: %SOURCE_HOST%
echo Database: %SOURCE_DB%
echo.
echo CANH BAO:
echo Chuc nang nay THAY THE 2 collection:
echo - patients
echo - medical_records
echo.
echo Du lieu thay doi sau thoi diem Backup
echo co the bi mat.
echo.

REM Khoa dia chi va database dich

if /I not "%SOURCE_URI%"=="mongodb+srv://cluster0.1rl5eeo.mongodb.net/" (
    echo [LOI] URI Atlas chinh khong hop le.
    pause
    goto MENU
)

if /I not "%SOURCE_DB%"=="medispace_db" (
    echo [LOI] Database dich khong hop le.
    pause
    goto MENU
)

REM Chon ban backup muon khoi phuc

echo Danh sach ban Backup:
dir "%BACKUP_ROOT%" /ad /b
echo.

set "STAMP="
set /p "STAMP=Nhap ten thu muc Backup: "

call :CHECK_BACKUP

if errorlevel 1 (
    echo [LOI] Ban Backup khong hop le.
    pause
    goto MENU
)

REM Luu duong dan ban backup duoc chon
set "SELECTED_BACKUP=%BACKUP_DIR%"

echo.
echo Ban Backup duoc chon:
echo %SELECTED_BACKUP%
echo.

REM Kiem tra dry run tren Atlas chinh

echo ============================================
echo KIEM TRA DRY RUN
echo ============================================
echo.

"%MONGORESTORE%" --uri="%SOURCE_URI%" --username="%SOURCE_USER%" --authenticationDatabase=admin --nsInclude="%SOURCE_DB%.patients" --nsInclude="%SOURCE_DB%.medical_records" --dryRun --verbose --dir="%SELECTED_BACKUP%"

if errorlevel 1 (
    echo.
    echo [LOI] Dry Run that bai.
    pause
    goto MENU
)

echo.
echo [OK] Dry Run hoan tat.
echo.

REM Yeu cau xac nhan dung ghi ung dung

set "PAUSED="
set /p "PAUSED=Da tam dung moi thao tac ghi FastAPI? Nhap YES: "

if not "%PAUSED%"=="YES" (
    echo Da huy Restore.
    pause
    goto MENU
)

REM Tao backup cuu ho truoc khi restore

echo.
echo ============================================
echo TAO BACKUP CUU HO DU LIEU HIEN TAI
echo ============================================
echo.

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "RESCUE_STAMP=%%i"

set "RESCUE_DIR=%BACKUP_ROOT%\rescue_%RESCUE_STAMP%"

if exist "%RESCUE_DIR%" (
    echo [LOI] Thu muc cuu ho da ton tai.
    pause
    goto MENU
)

mkdir "%RESCUE_DIR%"

if errorlevel 1 (
    echo [LOI] Khong tao duoc thu muc cuu ho.
    pause
    goto MENU
)

"%MONGODUMP%" --uri="%SOURCE_URI%" --username="%SOURCE_USER%" --authenticationDatabase=admin --db="%SOURCE_DB%" --out="%RESCUE_DIR%"

if errorlevel 1 (
    echo.
    echo [LOI] Khong tao duoc Backup cuu ho.
    echo Restore da bi huy.
    pause
    goto MENU
)

if not exist "%RESCUE_DIR%\%SOURCE_DB%\patients.bson" (
    echo [LOI] Backup cuu ho thieu patients.bson.
    pause
    goto MENU
)

if not exist "%RESCUE_DIR%\%SOURCE_DB%\medical_records.bson" (
    echo [LOI] Backup cuu ho thieu medical_records.bson.
    pause
    goto MENU
)

echo.
echo [OK] Da tao Backup cuu ho.
echo %RESCUE_DIR%
echo.

REM Xac nhan lan cuoi

echo ============================================
echo       XAC NHAN RESTORE LAN CUOI
echo ============================================
echo.
echo Cluster: %SOURCE_HOST%
echo Database: %SOURCE_DB%
echo.
echo Ban se RESTORE tu:
echo %SELECTED_BACKUP%
echo.
echo Ban cuu ho hien tai:
echo %RESCUE_DIR%
echo.
echo CANH BAO: Hai collection hien tai
echo se bi DROP truoc khi nap lai tu Backup.
echo.

set "CONFIRM_MAIN="
set /p "CONFIRM_MAIN=Nhap RESTORE-MEDISPACE-DB de dong y: "

if not "%CONFIRM_MAIN%"=="RESTORE-MEDISPACE-DB" (
    echo Da huy Restore.
    pause
    goto MENU
)

echo.
echo Dang Restore vao database chinh...
echo.

REM --drop chi ap dung cho 2 collection nsInclude
REM --stopOnError dung khi gap loi

"%MONGORESTORE%" --uri="%SOURCE_URI%" --username="%SOURCE_USER%" --authenticationDatabase=admin --nsInclude="%SOURCE_DB%.patients" --nsInclude="%SOURCE_DB%.medical_records" --drop --stopOnError --dir="%SELECTED_BACKUP%"

if errorlevel 1 (
    echo.
    echo [LOI] Restore that bai hoac chua hoan tat.
    echo.
    echo KHONG MO LAI UNG DUNG.
    echo Database co the dang thieu du lieu.
    echo.
    echo Ban cuu ho:
    echo %RESCUE_DIR%
    echo.
    echo Kiem tra Atlas truoc khi xu ly tiep.
    pause
    goto MENU
)

echo.
echo ============================================
echo RESTORE DA CHAY THANH CONG
echo ============================================
echo.
echo Database: %SOURCE_DB%
echo Backup: %SELECTED_BACKUP%
echo.
echo CAN KIEM TRA TREN COMPASS:
echo - So document patients
echo - So document medical_records
echo - Index va du lieu mau
echo - API FastAPI
echo.
echo Chi mo lai ghi du lieu sau khi kiem tra.
echo.
pause
goto MENU

REM ======================================
REM 12. THOAT
REM ======================================

:END
echo Da thoat.
endlocal
exit /b 0