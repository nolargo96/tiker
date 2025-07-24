@echo off
REM Tiker Dashboard Launcher for Windows仮想環境

echo ====================================
echo  Tiker ダッシュボードを起動します...
echo ====================================
echo.

REM Windows仮想環境のアクティベート
if exist win_venv\Scripts\activate.bat (
    call win_venv\Scripts\activate.bat
) else (
    echo エラー: Windows用仮想環境が見つかりません
    echo 先に setup_windows_venv.bat を実行してください
    pause
    exit /b 1
)

REM Streamlitを実行
python -m streamlit run run_dashboard.py --server.address 0.0.0.0 --server.port 8501

pause