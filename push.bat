@echo off
cd /d "%~dp0"
git add .
git commit -m "Initial commit: QQ Bot Webhook service"
git branch -M main
git push -u origin main --force
pause
