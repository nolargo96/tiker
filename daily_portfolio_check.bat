@echo off
echo ========================================
echo   日次ポートフォリオチェック
echo ========================================
echo.

set PYTHON=C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe
set PYTHONPATH=C:\Users\nolar\OneDrive\ドキュメント\code\my_dev_projects\tiker
set PYTHONIOENCODING=utf-8

echo [%date% %time%] チェック開始...
echo.

REM クイックレビューを実行
%PYTHON% scripts/portfolio_quick_review.py

REM 結果をログファイルに保存
echo. >> logs\daily_check_%date:~0,4%%date:~5,2%%date:~8,2%.log
echo [%date% %time%] 日次チェック完了 >> logs\daily_check_%date:~0,4%%date:~5,2%%date:~8,2%.log

REM アラート条件に該当する場合はレポート生成
REM （portfolio_quick_review.pyがアラートフラグファイルを生成する想定）
if exist "data\alerts\trigger_report.flag" (
    echo.
    echo ⚠️ アラート検出！詳細レポートを生成します...
    %PYTHON% src/portfolio/portfolio_master_report_hybrid.py
    del "data\alerts\trigger_report.flag"
)

echo.
echo ✅ 日次チェック完了
pause