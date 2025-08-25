# PowerShell script to start working on the EventoSys project
# This script activates the virtual environment and provides useful commands

Write-Host "EventoSys Project Starter" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""

# Check if we're already in the virtual environment
if ($env:VIRTUAL_ENV -eq $null) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
    
    # Verify activation
    if ($env:VIRTUAL_ENV -ne $null) {
        Write-Host "✓ Virtual environment activated successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already active" -ForegroundColor Green
}

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver          # Start the development server" -ForegroundColor White
Write-Host "  python manage.py migrate            # Apply database migrations" -ForegroundColor White
Write-Host "  python manage.py collectstatic      # Collect static files" -ForegroundColor White
Write-Host "  python verify_environment.py        # Verify environment setup" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Green