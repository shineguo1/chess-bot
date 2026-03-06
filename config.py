import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    qq_bot_appid: str
    qq_bot_secret: str
    qq_bot_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
