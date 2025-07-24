@echo off
REM Tiker Dash Dashboard Launcher
REM Plotly Dash版ダッシュボード起動スクリプト

echo ========================================
echo   Tiker Dash Dashboard を起動します
echo ========================================

REM Python環境の確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Pythonがインストールされていません
    echo Pythonをインストールしてから再度実行してください
    pause
    exit /b 1
)

REM 依存関係の確認とインストール
echo.
echo 依存関係を確認しています...
pip show dash >nul 2>&1
if %errorlevel% neq 0 (
    echo Dashがインストールされていません。インストールを開始します...
    pip install dash dash-bootstrap-components
)

REM ポートの確認
netstat -ano | findstr :8050 >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] ポート8050が既に使用されています
    echo 別のポートで起動します...
    set PORT=8051
) else (
    set PORT=8050
)

REM ダッシュボード起動
echo.
echo ダッシュボードを起動しています...
echo URL: http://localhost:%PORT%
echo.
echo ブラウザが自動的に開きます...
echo 終了するには Ctrl+C を押してください
echo.

REM ブラウザを開く（少し待ってから）
timeout /t 3 /nobreak >nul
start http://localhost:%PORT%

REM Dashアプリケーション実行
cd /d "%~dp0"
python src/web/dash_portfolio.py

pause