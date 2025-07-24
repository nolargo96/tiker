@echo off
REM Windows用仮想環境のセットアップ

echo ====================================
echo  Windows用仮想環境を作成します...
echo ====================================
echo.

REM 既存のwin_venvがあれば削除
if exist win_venv (
    echo 既存のwin_venvを削除します...
    rmdir /s /q win_venv
)

REM 仮想環境を作成
echo 仮想環境を作成中...
C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe -m venv win_venv

REM 仮想環境をアクティベート
echo.
echo 仮想環境をアクティベート中...
call win_venv\Scripts\activate.bat

REM 必要なパッケージをインストール
echo.
echo パッケージをインストール中...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ====================================
echo  セットアップが完了しました！
echo  launch_dashboard_win.bat を実行してください
echo ====================================

pause