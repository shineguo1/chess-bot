import httpx
import logging
from typing import Optional
from config import settings
from models import SendMessageResponse

logger = logging.getLogger(__name__)


class QQBotAPI:
    def __init__(self):
        self.base_url = "https://api.sgroup.qq.com"
        self.token_url = "https://bots.qq.com/app/getAppAccessToken"
        self.appid = settings.qq_bot_appid
        self.secret = settings.qq_bot_secret
        self._access_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        
        client = await self.get_client()
        
        payload = {
            "appId": self.appid,
            "clientSecret": self.secret
        }
        
        try:
            response = await client.post(self.token_url, json=payload)
            response.raise_for_status()
            data = response.json()
            self._access_token = data.get("access_token")
            logger.info("Successfully obtained access token")
            return self._access_token
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get access token: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise
    
    def get_auth_header(self, token: str) -> dict:
        return {
            "Authorization": f"QQBot {token}",
            "Content-Type": "application/json"
        }
    
    async def send_c2c_message(
        self, 
        openid: str, 
        content: str,
        msg_id: Optional[str] = None
    ) -> SendMessageResponse:
        client = await self.get_client()
        token = await self.get_access_token()
        
        url = f"{self.base_url}/v2/users/{openid}/messages"
        headers = self.get_auth_header(token)
        
        payload = {
            "content": content,
            "msg_type": 0
        }
        
        if msg_id:
            payload["msg_id"] = msg_id
        
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Message sent successfully to user {openid}")
            return SendMessageResponse(**data)
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(f"Failed to send message: {e.response.status_code} - {error_text}")
            if "token" in error_text.lower() or "expire" in error_text.lower():
                self._access_token = None
                logger.info("Token expired, will retry with new token")
            raise
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def send_group_message(
        self, 
        group_openid: str, 
        content: str,
        msg_id: Optional[str] = None
    ) -> SendMessageResponse:
        client = await self.get_client()
        token = await self.get_access_token()
        
        url = f"{self.base_url}/v2/groups/{group_openid}/messages"
        headers = self.get_auth_header(token)
        
        payload = {
            "content": content,
            "msg_type": 0
        }
        
        if msg_id:
            payload["msg_id"] = msg_id
        
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Message sent successfully to group {group_openid}")
            return SendMessageResponse(**data)
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(f"Failed to send group message: {e.response.status_code} - {error_text}")
            if "token" in error_text.lower() or "expire" in error_text.lower():
                self._access_token = None
                logger.info("Token expired, clearing cache for retry")
            raise
        except Exception as e:
            logger.error(f"Failed to send group message: {e}")
            raise
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


qq_bot_api = QQBotAPI()
