@echo off
echo ===============================================
echo Tiker Dashboard Pro - Windows起動ツール
echo ===============================================
echo.

:: Pythonのパス確認
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pythonが見つかりません。
    echo Pythonをインストールしてください。
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found: OK
echo.

:: 必要なパッケージのインストール確認
echo 必要なパッケージを確認しています...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Streamlitをインストールしています...
    pip install streamlit
)

pip show pandas >nul 2>&1
if errorlevel 1 (
    echo pandasをインストールしています...
    pip install pandas numpy
)

pip show yfinance >nul 2>&1
if errorlevel 1 (
    echo yfinanceをインストールしています...
    pip install yfinance
)

pip show plotly >nul 2>&1
if errorlevel 1 (
    echo plotlyをインストールしています...
    pip install plotly
)

echo.
echo ===============================================
echo ダッシュボードを起動しています...
echo ===============================================
echo.
echo ブラウザが自動的に開きます。
echo 開かない場合は手動で以下のURLにアクセスしてください：
echo.
echo   http://localhost:8501
echo.
echo 終了するには、このウィンドウを閉じるかCtrl+Cを押してください。
echo ===============================================
echo.

:: Streamlitを起動
streamlit run dashboard_pro.py

pause