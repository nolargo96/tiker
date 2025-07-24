@echo off
echo ========================================
echo   ポートフォリオ分析を実行します
echo ========================================
echo.

set PYTHON=C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe

echo 最新の株価データを取得して分析を開始...
echo.

%PYTHON% src/portfolio/portfolio_master_report_hybrid.py

echo.
echo 分析が完了しました！
echo.
echo レポートの場所:
echo reports\html\portfolio_hybrid_report_[日付].html
echo.
echo ブラウザで開きます...

for /f "tokens=*" %%i in ('dir /b /od reports\html\portfolio_hybrid_report_*.html') do set LATEST=%%i
start "" "reports\html\%LATEST%"

pause