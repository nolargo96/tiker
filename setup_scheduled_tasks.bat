@echo off
echo ========================================
echo   タスクスケジューラー設定
echo ========================================
echo.

REM 日次チェック（毎朝9:00）
schtasks /create /tn "TikerDailyCheck" /tr "%cd%\daily_portfolio_check.bat" /sc daily /st 09:00 /f

REM 週次レポート（毎週月曜9:30）
schtasks /create /tn "TikerWeeklyReport" /tr "%cd%\run_portfolio_analysis.bat" /sc weekly /d MON /st 09:30 /f

echo.
echo ✅ スケジュールタスクを設定しました：
echo    - 日次チェック: 毎日 9:00
echo    - 週次レポート: 毎週月曜 9:30
echo.
echo 設定を確認するには以下を実行:
echo schtasks /query /tn "TikerDailyCheck"
echo schtasks /query /tn "TikerWeeklyReport"
echo.
pause