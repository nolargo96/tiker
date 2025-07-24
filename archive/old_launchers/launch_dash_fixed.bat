@echo off
REM Fixed Dash launcher with proper error handling

echo ========================================
echo   Tiker Dash Dashboard - Fixed Version
echo ========================================
echo.

REM Find Python executable
set PYTHON_PATH=C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found at %PYTHON_PATH%
    echo Trying to find Python in PATH...
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_PATH=python
    ) else (
        echo [ERROR] Python not found. Please install Python.
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_PATH%
echo.

REM Test dependencies
echo Testing dependencies...
%PYTHON_PATH% test_dash.py
echo.

REM Install missing dependencies
echo Installing/updating dependencies...
%PYTHON_PATH% -m pip install --upgrade pip >nul 2>&1
%PYTHON_PATH% -m pip install "numpy>=1.24.0,<2.0.0" pandas yfinance dash dash-bootstrap-components plotly

echo.
echo Starting Dash dashboard...
echo.

REM Run the Dash app
cd /d "%~dp0"
%PYTHON_PATH% run_dash.py

pause