@echo off
echo ========================================
echo   Minimal Test Dashboard
echo ========================================
echo.

set PYTHON=C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe

echo Installing Flask if needed...
%PYTHON% -m pip install flask >nul 2>&1

echo.
echo Starting test dashboard on http://localhost:5555
echo.

%PYTHON% minimal_test_dashboard.py

pause