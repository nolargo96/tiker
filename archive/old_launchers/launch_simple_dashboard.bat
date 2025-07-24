@echo off
REM ========================================
REM Tiker Simple Dashboard Launcher
REM Flask + vanilla JavaScript版
REM ========================================

echo ========================================
echo   Tiker Simple Dashboard
echo   Flask + vanilla JavaScript版
echo ========================================
echo.

REM Pythonパスの設定
set PYTHON_PATH=C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe

REM Pythonの存在確認
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Pythonが見つかりません: %PYTHON_PATH%
    echo Pythonをインストールしてください。
    pause
    exit /b 1
)

echo Pythonを確認しました: %PYTHON_PATH%
echo.

REM 依存関係のインストール
echo 必要なパッケージを確認しています...
%PYTHON_PATH% -m pip install --quiet flask yfinance pandas

REM ポートの確認
set PORT=5000
netstat -an | findstr :5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] ポート5000が使用中です。ポート5001を使用します。
    set PORT=5001
)

REM 環境変数の設定
set FLASK_PORT=%PORT%

REM ダッシュボードの起動
echo.
echo ========================================
echo ダッシュボードを起動しています...
echo URL: http://localhost:%PORT%
echo.
echo 3秒後にブラウザが自動的に開きます...
echo 終了するには Ctrl+C を押してください
echo ========================================
echo.

REM ブラウザを遅延起動
timeout /t 3 /nobreak >nul
start http://localhost:%PORT%

REM Flaskアプリケーションの実行
cd /d "%~dp0"
%PYTHON_PATH% src\web\simple_dashboard.py

pause