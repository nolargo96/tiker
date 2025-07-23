@echo off
REM Tiker Dashboard 起動スクリプト (Windows用)

echo 🚀 Tiker Interactive Dashboard を起動します...
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonが見つかりません。インストールしてください。
    pause
    exit /b 1
)

REM Streamlitがインストールされているか確認
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 必要なライブラリをインストールしています...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ インストールに失敗しました。
        pause
        exit /b 1
    )
)

echo.
echo どちらのダッシュボードを起動しますか？
echo 1) 基本版 (dashboard.py)
echo 2) 強化版 - 4専門家統合型 (dashboard_enhanced.py) [推奨]
echo.
set /p choice="選択してください (1 or 2): "

if "%choice%"=="1" (
    echo 📊 基本版ダッシュボードを起動中...
    python -m streamlit run dashboard.py
) else (
    echo 🚀 強化版ダッシュボードを起動中...
    python -m streamlit run dashboard_enhanced.py
)

pause