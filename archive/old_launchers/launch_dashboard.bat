@echo off
REM Tiker Dashboard Launcher for Windows
REM Windowsから簡単にダッシュボードを起動するバッチファイル

echo ====================================
echo  Tiker ダッシュボードを起動します...
echo ====================================
echo.

REM 仮想環境のアクティベート
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo エラー: 仮想環境が見つかりません
    echo 先に仮想環境を作成してください
    pause
    exit /b 1
)

REM Streamlitを実行
python -m streamlit run run_dashboard.py --server.address 0.0.0.0 --server.port 8501

pause