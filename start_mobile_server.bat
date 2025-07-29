@echo off
echo ===============================================
echo   ポートフォリオ モバイルサーバー起動
echo ===============================================
echo.

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM 必要なパッケージの確認とインストール
echo 必要なパッケージを確認中...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Flaskをインストール中...
    pip install flask
)

pip show qrcode >nul 2>&1
if errorlevel 1 (
    echo QRコードライブラリをインストール中...
    pip install qrcode[pil]
)

echo.
echo サーバーを起動中...
echo.

REM モバイルサーバーを起動
python mobile_server.py

pause