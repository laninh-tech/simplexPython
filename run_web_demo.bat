@echo off
REM Chay web demo simplexPython (viet bang Python va Flask)

echo.
echo ==========================================
echo   simplexPython Web Demo
echo ==========================================
echo.

python -m pip list | findstr /i flask > nul
if errorlevel 1 (
    echo Cai dat Flask & numpy...
    pip install -r "%~dp0requirements.txt"
    echo.
)

cd /d "%~dp0.."
set PYTHONPATH=%CD%

echo Dang dung server cu tren cong 8080 (neu co)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /LISTENING ^| findstr :8080') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Khoi dong server MOI...
echo Mo trinh duyet: http://localhost:8080
echo (Nhan Ctrl+F5 de tai lai trang neu van thay giao dien cu)
echo.
python -m simplexPython.menu.app

pause
