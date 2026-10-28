
@echo off
setlocal DisableDelayedExpansion

REM ============================================
REM MEDISPACE - AUTOMATIC MONGODB BACKUP
REM Chi Backup, KHONG Restore
REM ============================================

set "MONGODUMP=D:\MongoDBTools\bin\mongodump.exe"

set "SOURCE_URI=mongodb+srv://cluster0.1rl5eeo.mongodb.net/"
set "SOURCE_DB=medispace_db"

REM Tai khoan Atlas chi co quyen doc va Backup
set "SOURCE_USER=sv3-fe"

REM File chua mat khau duoc bao ve
set "AUTH_CONFIG=D:\MediSpaceSecrets\mongodump.yaml"

set "BACKUP_ROOT=D:\medispace\backup"
set "LOG_ROOT=D:\medispace\backup_logs"

REM ============================================
REM 1. KIEM TRA DIEU KIEN
REM ============================================

if not exist "%MONGODUMP%" exit /b 10
if not exist "%AUTH_CONFIG%" exit /b 11

if not exist "%BACKUP_ROOT%" mkdir "%BACKUP_ROOT%"
if not exist "%LOG_ROOT%" mkdir "%LOG_ROOT%"

if not exist "%BACKUP_ROOT%\" exit /b 12
if not exist "%LOG_ROOT%\" exit /b 13

REM ============================================
REM 2. TAO TIMESTAMP
REM ============================================

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"

if not defined STAMP exit /b 14

set "FINAL_DIR=%BACKUP_ROOT%\auto_%STAMP%"
set "WORK_DIR=%BACKUP_ROOT%\auto_%STAMP%.incomplete"
set "LOG_FILE=%LOG_ROOT%\auto_%STAMP%.log"

if exist "%FINAL_DIR%" exit /b 15
if exist "%WORK_DIR%" exit /b 16

mkdir "%WORK_DIR%"
if errorlevel 1 exit /b 17

echo ============================================ > "%LOG_FILE%"
echo MEDISPACE AUTOMATIC BACKUP >> "%LOG_FILE%"
echo Timestamp: %STAMP% >> "%LOG_FILE%"
echo Database: %SOURCE_DB% >> "%LOG_FILE%"
echo ============================================ >> "%LOG_FILE%"

REM ============================================
REM 3. CHAY MONGODUMP
REM ============================================

"%MONGODUMP%" --config="%AUTH_CONFIG%" --uri="%SOURCE_URI%" --username="%SOURCE_USER%" --authenticationDatabase=admin --db="%SOURCE_DB%" --out="%WORK_DIR%" >> "%LOG_FILE%" 2>&1

if errorlevel 1 goto BACKUP_FAILED

REM ============================================
REM 4. KIEM TRA FILE BACKUP
REM ============================================

set "DATA_DIR=%WORK_DIR%\%SOURCE_DB%"

if not exist "%DATA_DIR%\patients.bson" goto BACKUP_FAILED
if not exist "%DATA_DIR%\medical_records.bson" goto BACKUP_FAILED
if not exist "%DATA_DIR%\patients.metadata.json" goto BACKUP_FAILED
if not exist "%DATA_DIR%\medical_records.metadata.json" goto BACKUP_FAILED

for %%F in ("%DATA_DIR%\patients.bson") do if %%~zF LEQ 0 goto BACKUP_FAILED
for %%F in ("%DATA_DIR%\medical_records.bson") do if %%~zF LEQ 0 goto BACKUP_FAILED

REM ============================================
REM 5. DANH DAU BACKUP HOAN TAT
REM ============================================

move "%WORK_DIR%" "%FINAL_DIR%" >> "%LOG_FILE%" 2>&1

if errorlevel 1 goto BACKUP_FAILED

echo. >> "%LOG_FILE%"
echo [SUCCESS] Backup completed. >> "%LOG_FILE%"
echo Directory: %FINAL_DIR% >> "%LOG_FILE%"

exit /b 0

REM ============================================
REM 6. XU LY LOI
REM ============================================

:BACKUP_FAILED
echo. >> "%LOG_FILE%"
echo [FAILED] Backup incomplete or invalid. >> "%LOG_FILE%"
echo Work directory: %WORK_DIR% >> "%LOG_FILE%"
echo Previous backups remain unchanged. >> "%LOG_FILE%"

exit /b 1
