@echo off
echo 启动 QQ Bot 服务...
echo 服务地址: http://0.0.0.0:8080
echo API文档: http://localhost:8080/docs
echo.

cd /d "%~dp0"

python -m uvicorn main:app --host 0.0.0.0 --port 8080
