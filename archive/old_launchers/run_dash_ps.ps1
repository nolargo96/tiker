# PowerShell script to run Dash dashboard
Write-Host "Starting Tiker Dash Dashboard..." -ForegroundColor Green
Write-Host ""

$pythonPath = "C:\Users\nolar\AppData\Local\Programs\Python\Python313\python.exe"

if (Test-Path $pythonPath) {
    Write-Host "Python found at: $pythonPath" -ForegroundColor Yellow
    
    # Run the simple test first
    Write-Host "Running simple test..." -ForegroundColor Cyan
    & $pythonPath simple_dash_test.py
} else {
    Write-Host "Python not found at expected location" -ForegroundColor Red
    Write-Host "Trying to find Python in PATH..."
    
    try {
        python --version
        Write-Host "Running with system Python..." -ForegroundColor Yellow
        python simple_dash_test.py
    } catch {
        Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Read-Host "Press Enter to exit"