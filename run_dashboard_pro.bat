@echo off
echo ===============================================
echo Tiker Dashboard Pro Ultimate - 起動スクリプト
echo ===============================================
echo.

:: Python環境の確認
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pythonがインストールされていません
    echo Pythonをインストールしてください: https://www.python.org/
    pause
    exit /b 1
)

:: 必要なパッケージの確認とインストール
echo [1/4] 必要なパッケージを確認しています...
echo.

:: Streamlitのインストール確認
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Streamlitをインストールしています...
    pip install streamlit
)

:: その他の必要なパッケージ
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo pandasをインストールしています...
    pip install pandas
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo numpyをインストールしています...
    pip install numpy
)

python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo yfinanceをインストールしています...
    pip install yfinance
)

python -c "import plotly" >nul 2>&1
if errorlevel 1 (
    echo plotlyをインストールしています...
    pip install plotly
)

python -c "import xlsxwriter" >nul 2>&1
if errorlevel 1 (
    echo xlsxwriterをインストールしています...
    pip install xlsxwriter
)

python -c "import reportlab" >nul 2>&1
if errorlevel 1 (
    echo reportlabをインストールしています...
    pip install reportlab
)

python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo matplotlibをインストールしています...
    pip install matplotlib
)

python -c "import seaborn" >nul 2>&1
if errorlevel 1 (
    echo seabornをインストールしています...
    pip install seaborn
)

echo.
echo [2/4] パッケージのインストールが完了しました
echo.

:: ダッシュボードの選択
echo ===============================================
echo どのダッシュボードを起動しますか？
echo ===============================================
echo 1. Dashboard Pro Ultimate (最新・究極版)
echo 2. Dashboard Enhanced (強化版)
echo 3. Dashboard Basic (基本版)
echo 4. Dashboard Ultra Simple (超シンプル版)
echo ===============================================
set /p choice="番号を選択してください (1-4): "

if "%choice%"=="1" (
    set dashboard=dashboard_pro.py
    echo.
    echo [3/4] Dashboard Pro Ultimate を起動します...
) else if "%choice%"=="2" (
    set dashboard=dashboard_enhanced.py
    echo.
    echo [3/4] Dashboard Enhanced を起動します...
) else if "%choice%"=="3" (
    set dashboard=dashboard.py
    echo.
    echo [3/4] Dashboard Basic を起動します...
) else if "%choice%"=="4" (
    set dashboard=dashboard_ultra_simple.py
    echo.
    echo [3/4] Dashboard Ultra Simple を起動します...
) else (
    echo.
    echo [ERROR] 無効な選択です
    pause
    exit /b 1
)

:: ファイルの存在確認
if not exist "%dashboard%" (
    echo.
    echo [ERROR] %dashboard% が見つかりません
    echo 現在のディレクトリ: %CD%
    pause
    exit /b 1
)

echo.
echo [4/4] Streamlitサーバーを起動しています...
echo.
echo ===============================================
echo ブラウザが自動的に開きます
echo 開かない場合は以下のURLにアクセスしてください:
echo http://localhost:8501
echo.
echo 終了するには Ctrl+C を押してください
echo ===============================================
echo.

:: Streamlitの起動
streamlit run %dashboard%

pause