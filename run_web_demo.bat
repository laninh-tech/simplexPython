@echo off
REM Chay web demo simplexPython (viet bang Python va Flask)
chcp 65001 > nul

echo.
echo ==========================================
echo   simplexPython Web Demo - QHTT Studio
echo ==========================================
echo.

python -m pip list | findstr /i "flask" > nul
if errorlevel 1 (
    echo Đang cài đặt các thư viện cần thiết (Flask, numpy)...
    pip install -r "%~dp0requirements.txt"
    echo.
)

cd /d "%~dp0.."
set PYTHONPATH=%CD%

echo Đang dọn dẹp tiến trình cũ chạy trên cổng 8080 (nếu có)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":8080"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Khởi động Server Flask mới...
echo Mở trình duyệt tại địa chỉ: http://localhost:8080
echo (Nhấn Ctrl+F5 để tải lại trang nếu vẫn thấy giao diện cũ)
echo.
python -m simplexPython.menu.app

pause
