# Tiker Simple Dashboard Launcher (PowerShell版)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tiker Simple Dashboard" -ForegroundColor Yellow
Write-Host "  Flask + vanilla JavaScript版" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pythonパスの設定
$pythonPath = "C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe"

# Pythonの存在確認
if (!(Test-Path $pythonPath)) {
    Write-Host "[ERROR] Pythonが見つかりません: $pythonPath" -ForegroundColor Red
    Write-Host "Pythonをインストールしてください。" -ForegroundColor Red
    Read-Host "Enterキーを押して終了"
    exit 1
}

Write-Host "Pythonを確認しました: $pythonPath" -ForegroundColor Green
Write-Host ""

# 依存関係のインストール
Write-Host "必要なパッケージを確認しています..." -ForegroundColor Yellow
& $pythonPath -m pip install --quiet flask yfinance pandas

# ポートの確認
$port = 5000
$portInUse = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet 2>$null
if ($portInUse) {
    Write-Host "[INFO] ポート5000が使用中です。ポート5001を使用します。" -ForegroundColor Yellow
    $port = 5001
}

# 環境変数の設定
$env:FLASK_PORT = $port

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ダッシュボードを起動しています..." -ForegroundColor Green
Write-Host "URL: http://localhost:$port" -ForegroundColor Yellow
Write-Host ""
Write-Host "3秒後にブラウザが自動的に開きます..." -ForegroundColor Cyan
Write-Host "終了するには Ctrl+C を押してください" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ブラウザを遅延起動
Start-Sleep -Seconds 3
Start-Process "http://localhost:$port"

# Flaskアプリケーションの実行
Set-Location $PSScriptRoot
& $pythonPath "src\web\simple_dashboard.py"