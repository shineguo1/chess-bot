Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "QQ Bot Webhook 测试脚本 (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$BaseUrl = "http://localhost:8080"

Write-Host ""
Write-Host "1. 测试健康检查端点..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. 测试回调地址验证 (op=13)..." -ForegroundColor Yellow
try {
    $body = @{
        id = "test_validation"
        op = 13
        d = @{
            plain_token = "Arq0D5A61EgUu4OxUvOp"
            event_ts = "1725442341"
        }
    } | ConvertTo-Json -Depth 3
    
    $headers = @{
        "Content-Type" = "application/json"
        "X-Bot-Appid" = "test_app_id"
    }
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/webhook" -Method Post -Body $body -Headers $headers
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. 测试 /hello 命令 (C2C_MESSAGE_CREATE)..." -ForegroundColor Yellow
try {
    $body = @{
        id = "test_msg_id"
        op = 0
        s = 1
        t = "C2C_MESSAGE_CREATE"
        d = @{
            id = "ROBOT1.0_test_msg"
            author = @{
                user_openid = "TEST_USER_OPENID"
            }
            content = "/hello"
            timestamp = "2023-11-06T13:37:18+08:00"
        }
    } | ConvertTo-Json -Depth 3
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/webhook" -Method Post -Body $body -Headers $headers
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. 测试 /chess-insight 命令 (C2C_MESSAGE_CREATE)..." -ForegroundColor Yellow
try {
    $body = @{
        id = "test_chess_msg"
        op = 0
        s = 2
        t = "C2C_MESSAGE_CREATE"
        d = @{
            id = "ROBOT1.0_chess_msg"
            author = @{
                user_openid = "TEST_USER_OPENID"
            }
            content = "/chess-insight -u TZZRoiOXTmVPU7FLM8YyKKzf1xF2 -c 10"
            timestamp = "2023-11-06T13:37:18+08:00"
        }
    } | ConvertTo-Json -Depth 3
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/webhook" -Method Post -Body $body -Headers $headers
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. 测试群聊@消息事件 (GROUP_AT_MESSAGE_CREATE)..." -ForegroundColor Yellow
try {
    $body = @{
        id = "test_group_msg"
        op = 0
        s = 3
        t = "GROUP_AT_MESSAGE_CREATE"
        d = @{
            id = "ROBOT1.0_group_msg"
            author = @{
                member_openid = "TEST_MEMBER_OPENID"
            }
            content = " /hello"
            group_openid = "TEST_GROUP_OPENID"
            timestamp = "2023-11-06T13:37:18+08:00"
        }
    } | ConvertTo-Json -Depth 3
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/webhook" -Method Post -Body $body -Headers $headers
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "测试完成!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
