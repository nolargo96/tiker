@echo off
echo ========================================
echo   最新のHTMLレポートを開きます
echo ========================================
echo.

cd /d "%~dp0"

REM 最新のポートフォリオレポートを探す
for /f "tokens=*" %%i in ('dir /b /od reports\html\portfolio_*.html 2^>nul') do set LATEST_PORTFOLIO=%%i

REM 最新の個別銘柄レポートを探す
for /f "tokens=*" %%i in ('dir /b /od reports\html\TSLA_*.html 2^>nul') do set LATEST_TSLA=%%i

if defined LATEST_PORTFOLIO (
    echo 最新のポートフォリオレポート: %LATEST_PORTFOLIO%
    start "" "reports\html\%LATEST_PORTFOLIO%"
) else (
    echo ポートフォリオレポートが見つかりません
)

echo.
echo その他のレポート:
dir /b reports\html\*.html 2^>nul | findstr /v "script.js styles.css"

echo.
echo 上記のレポートを開くには、reports\html\ フォルダを参照してください
echo.

pause