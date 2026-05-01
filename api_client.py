import httpx
import logging
import asyncio
from typing import Optional, Callable, Awaitable, TypeVar
from config import settings
from models import SendMessageResponse

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QQBotAPI:
    def __init__(self):
        self.base_url = "https://api.sgroup.qq.com"
        self.token_url = "https://bots.qq.com/app/getAppAccessToken"
        self.appid = settings.qq_bot_appid
        self.secret = settings.qq_bot_secret
        self._access_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
        self.max_retries = 3
        self.retry_delay = 0.5  # 500ms
    
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
    
    async def _retry_with_backoff(
        self,
        func: Callable[[], Awaitable[T]],
        should_retry: Optional[Callable[[Exception], bool]] = None
    ) -> T:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed")
                    raise
                if should_retry and not should_retry(e):
                    raise
                await asyncio.sleep(self.retry_delay)
                logger.info(f"Retrying... Attempt {attempt + 2}/{self.max_retries}")
        raise last_exception
    
    async def send_c2c_message(
        self, 
        openid: str, 
        content: str,
        msg_id: Optional[str] = None
    ) -> SendMessageResponse:
        async def _send():
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
            
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Message sent successfully to user {openid}")
            return SendMessageResponse(**data)
        
        def _should_retry(e: Exception) -> bool:
            if isinstance(e, httpx.HTTPStatusError):
                if 400 <= e.response.status_code < 500:
                    error_text = e.response.text
                    try:
                        error_data = e.response.json()
                        error_code = error_data.get("err_code")
                        if error_code == 40054005:
                            logger.warning("Message deduplicated, not retrying")
                            return False
                    except:
                        pass
                    
                    if "token" in error_text.lower() or "expire" in error_text.lower():
                        self._access_token = None
                        logger.info("Token expired, clearing cache for retry")
                        return True
                if 500 <= e.response.status_code < 600:
                    if "token" in error_text.lower() or "expire" in error_text.lower():
                        self._access_token = None
                        logger.info("Token expired in server error, clearing cache for retry")
                        return True
                    logger.info(f"Server error {e.response.status_code}, retrying")
                    return True
            return False
        
        try:
            return await self._retry_with_backoff(_send, _should_retry)
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to send message: {e.response.status_code} - {e.response.text}")
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
        async def _send():
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
            
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Message sent successfully to group {group_openid}")
            return SendMessageResponse(**data)
        
        def _should_retry(e: Exception) -> bool:
            if isinstance(e, httpx.HTTPStatusError):
                if 400 <= e.response.status_code < 500:
                    error_text = e.response.text
                    try:
                        error_data = e.response.json()
                        error_code = error_data.get("err_code")
                        if error_code == 40054005:
                            logger.warning("Message deduplicated, not retrying")
                            return False
                    except:
                        pass
                    
                    if "token" in error_text.lower() or "expire" in error_text.lower():
                        self._access_token = None
                        logger.info("Token expired, clearing cache for retry")
                        return True
                if 500 <= e.response.status_code < 600:
                    if "token" in error_text.lower() or "expire" in error_text.lower():
                        self._access_token = None
                        logger.info("Token expired in server error, clearing cache for retry")
                        return True
                    logger.info(f"Server error {e.response.status_code}, retrying")
                    return True
            return False
        
        try:
            return await self._retry_with_backoff(_send, _should_retry)
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to send group message: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to send group message: {e}")
            raise
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


qq_bot_api = QQBotAPI()
