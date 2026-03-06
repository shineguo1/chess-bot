# QQ机器人Webhook服务

基于QQ机器人API v2开发的Webhook服务，支持单聊和群聊场景的命令响应。

## 支持的命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/hello` | 测试命令，返回 "hello world" | `/hello` |
| `/chess-insight` | 查询Pokemon Auto Chess战绩统计 | `/chess-insight -u 用户ID -c 局数` |

## 环境要求

- Python 3.9+
- Linux服务器（推荐Ubuntu 20.04+）
- 公网IP或域名（需配置HTTPS）

## 快速开始

### 1. 安装依赖

```bash
cd /opt/qq-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的机器人信息：

```env
QQ_BOT_APPID=你的机器人AppID
QQ_BOT_SECRET=你的机器人AppSecret
QQ_BOT_TOKEN=你的机器人Token（可选）
```

### 3. 启动服务

**开发环境：**
```bash
python main.py
```

**生产环境（使用Gunicorn + Uvicorn）：**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

## QQ开放平台配置

### 1. 创建机器人

访问 [QQ开放平台](https://q.qq.com/) 创建机器人，获取：
- AppID
- AppSecret

### 2. 配置回调地址

在机器人管理后台配置Webhook回调地址：

```
https://your-domain.com/webhook
```

支持的端口：`80`, `443`, `8080`, `8443`

### 3. 订阅事件

在管理后台订阅以下事件：
- `C2C_MESSAGE_CREATE` - 单聊消息
- `GROUP_AT_MESSAGE_CREATE` - 群聊@消息

## HTTPS配置（生产环境必需）

### 使用Nginx反向代理

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 使用Systemd管理服务

创建服务文件 `/etc/systemd/system/qq-bot.service`：

```ini
[Unit]
Description=QQ Bot Webhook Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/qq-bot
Environment="PATH=/opt/qq-bot/venv/bin"
ExecStart=/opt/qq-bot/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable qq-bot
sudo systemctl start qq-bot
sudo systemctl status qq-bot
```

## 日志

日志文件位置：`logs/qq-bot.log`

- 单文件最大10MB
- 保留5个备份文件

查看实时日志：
```bash
tail -f logs/qq-bot.log
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/webhook` | POST | QQ平台回调地址 |

## 本地测试（无需域名）

### 方式一：使用curl命令

**1. 启动服务**
```bash
# Linux/Mac
bash start_server.sh

# Windows
start_server.bat

# 或直接运行
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

**2. 运行测试脚本**
```bash
# Linux/Mac
bash test_curl.sh

# Windows PowerShell
.\test_curl.ps1

# Windows CMD
curl http://localhost:8080/health
```

**3. 手动curl测试**

健康检查：
```bash
curl http://localhost:8080/health
```

回调验证测试：
```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_validation","op":13,"d":{"plain_token":"Arq0D5A61EgUu4OxUvOp","event_ts":"1725442341"}}'
```

单聊消息测试：
```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_msg","op":0,"s":1,"t":"C2C_MESSAGE_CREATE","d":{"id":"msg123","author":{"user_openid":"TEST_USER"},"content":"/insight","timestamp":"2023-11-06T13:37:18+08:00"}}'
```

### 方式二：使用内网穿透（对接QQ平台）

**使用 ngrok（推荐）：**
```bash
# 安装 ngrok 后运行
ngrok http 8080
```

会得到类似 `https://xxxx.ngrok-free.app` 的公网地址，然后在QQ开放平台配置：
```
https://xxxx.ngrok-free.app/webhook
```

**使用 frp：**
```bash
# 需要有公网服务器
frpc -c frpc.ini
```

### 方式三：使用服务器IP

如果有公网服务器，可以直接使用IP：
```
http://你的服务器公网IP:8080/webhook
```

> 注意：QQ平台要求生产环境使用HTTPS，开发测试阶段可以使用HTTP

## 测试验证

### 1. 健康检查

```bash
curl http://localhost:8080/health
```

预期响应：
```json
{"status": "healthy", "service": "qq-bot"}
```

### 2. API文档

访问 http://localhost:8080/docs 查看交互式API文档

### 3. 命令测试

在手机QQ中：
1. 单聊：直接发送 `/insight`
2. 群聊：@机器人 后发送 `/insight`

预期响应：`hello world`

## 常见问题

### Q: 回调地址验证失败？
A: 检查：
1. HTTPS证书是否正确
2. 端口是否在允许列表内（80/443/8080/8443）
3. 服务是否正常运行

### Q: 消息发送失败？
A: 检查：
1. AppID和AppSecret是否正确
2. 是否订阅了对应事件
3. 查看日志获取详细错误信息

### Q: 签名验证失败？
A: 确保：
1. AppSecret配置正确
2. 使用原始请求体进行验证（不要重新序列化）

## 项目结构

```
qq-bot/
├── main.py              # FastAPI应用入口
├── config.py            # 配置管理
├── models.py            # 数据模型
├── signature.py         # Ed25519签名验证
├── api_client.py        # QQ API客户端
├── logger.py            # 日志配置
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量模板
├── logs/                # 日志目录
└── README.md            # 本文档
```
