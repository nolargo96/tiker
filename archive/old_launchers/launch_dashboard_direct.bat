@echo off
REM Tiker Dashboard Launcher - Direct Python
REM システムのPython 3.13を直接使用

echo ====================================
echo  Tiker ダッシュボードを起動します...
echo ====================================
echo.

REM システムのPython 3.13を使用
C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run run_dashboard.py --server.address 0.0.0.0 --server.port 8501

pause