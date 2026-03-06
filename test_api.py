import asyncio
import httpx
import json


async def test_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/health")
        print(f"Health check: {response.status_code}")
        print(response.json())


async def test_webhook_validation():
    payload = {
        "id": "test_validation",
        "op": 13,
        "d": {
            "plain_token": "Arq0D5A61EgUu4OxUvOp",
            "event_ts": "1725442341"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/webhook",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Bot-Appid": "test_app_id"
            }
        )
        print(f"Validation response: {response.status_code}")
        print(response.json())


async def test_c2c_message():
    payload = {
        "id": "test_msg_id",
        "op": 0,
        "s": 1,
        "t": "C2C_MESSAGE_CREATE",
        "d": {
            "id": "ROBOT1.0_test_msg",
            "author": {
                "user_openid": "TEST_USER_OPENID"
            },
            "content": "/insight",
            "timestamp": "2023-11-06T13:37:18+08:00"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/webhook",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Bot-Appid": "test_app_id"
            }
        )
        print(f"C2C message response: {response.status_code}")
        print(response.json())


async def main():
    print("=== Testing Health Endpoint ===")
    await test_health()
    
    print("\n=== Testing Webhook Validation ===")
    await test_webhook_validation()
    
    print("\n=== Testing C2C Message (without signature) ===")
    await test_c2c_message()


if __name__ == "__main__":
    asyncio.run(main())
