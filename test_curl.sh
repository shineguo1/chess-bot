#!/bin/bash

echo "=========================================="
echo "QQ Bot Webhook 测试脚本"
echo "=========================================="

BASE_URL="http://localhost:8080"

echo ""
echo "1. 测试健康检查端点..."
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo ""

echo ""
echo "2. 测试回调地址验证 (op=13)..."
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_validation","op":13,"d":{"plain_token":"Arq0D5A61EgUu4OxUvOp","event_ts":"1725442341"}}' | jq . 2>/dev/null || \
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_validation","op":13,"d":{"plain_token":"Arq0D5A61EgUu4OxUvOp","event_ts":"1725442341"}}'
echo ""

echo ""
echo "3. 测试 /hello 命令 (C2C_MESSAGE_CREATE)..."
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_msg_id","op":0,"s":1,"t":"C2C_MESSAGE_CREATE","d":{"id":"ROBOT1.0_test_msg","author":{"user_openid":"TEST_USER_OPENID"},"content":"/hello","timestamp":"2023-11-06T13:37:18+08:00"}}' | jq . 2>/dev/null || \
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_msg_id","op":0,"s":1,"t":"C2C_MESSAGE_CREATE","d":{"id":"ROBOT1.0_test_msg","author":{"user_openid":"TEST_USER_OPENID"},"content":"/hello","timestamp":"2023-11-06T13:37:18+08:00"}}'
echo ""

echo ""
echo "4. 测试 /chess-insight 命令 (C2C_MESSAGE_CREATE)..."
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_chess_msg","op":0,"s":2,"t":"C2C_MESSAGE_CREATE","d":{"id":"ROBOT1.0_chess_msg","author":{"user_openid":"TEST_USER_OPENID"},"content":"/chess-insight -u TZZRoiOXTmVPU7FLM8YyKKzf1xF2 -c 10","timestamp":"2023-11-06T13:37:18+08:00"}}' | jq . 2>/dev/null || \
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_chess_msg","op":0,"s":2,"t":"C2C_MESSAGE_CREATE","d":{"id":"ROBOT1.0_chess_msg","author":{"user_openid":"TEST_USER_OPENID"},"content":"/chess-insight -u TZZRoiOXTmVPU7FLM8YyKKzf1xF2 -c 10","timestamp":"2023-11-06T13:37:18+08:00"}}'
echo ""

echo ""
echo "5. 测试群聊@消息事件 (GROUP_AT_MESSAGE_CREATE)..."
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_group_msg","op":0,"s":3,"t":"GROUP_AT_MESSAGE_CREATE","d":{"id":"ROBOT1.0_group_msg","author":{"member_openid":"TEST_MEMBER_OPENID"},"content":" /hello","group_openid":"TEST_GROUP_OPENID","timestamp":"2023-11-06T13:37:18+08:00"}}' | jq . 2>/dev/null || \
curl -s -X POST "$BASE_URL/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Appid: test_app_id" \
  -d '{"id":"test_group_msg","op":0,"s":3,"t":"GROUP_AT_MESSAGE_CREATE","d":{"id":"ROBOT1.0_group_msg","author":{"member_openid":"TEST_MEMBER_OPENID"},"content":" /hello","group_openid":"TEST_GROUP_OPENID","timestamp":"2023-11-06T13:37:18+08:00"}}'
echo ""

echo ""
echo "=========================================="
echo "测试完成!"
echo "=========================================="
