Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8080" -NoNewWindow -WorkingDirectory "f:\workspace\qq-bot"
Start-Sleep -Seconds 3
Write-Host "Service started. Testing..."
Invoke-RestMethod -Uri "http://localhost:8080/health"
