from pydantic import BaseModel
from typing import Optional, List, Any


class WebhookPayload(BaseModel):
    id: str
    op: int
    d: Any
    s: Optional[int] = None
    t: Optional[str] = None


class ValidationRequest(BaseModel):
    plain_token: str
    event_ts: str


class ValidationResponse(BaseModel):
    plain_token: str
    signature: str


class Author(BaseModel):
    user_openid: Optional[str] = None
    member_openid: Optional[str] = None


class Attachment(BaseModel):
    content_type: str
    filename: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    size: Optional[int] = None
    url: Optional[str] = None


class C2CMessageEvent(BaseModel):
    id: str
    author: Author
    content: str
    timestamp: str
    attachments: Optional[List[Attachment]] = None


class GroupAtMessageEvent(BaseModel):
    id: str
    author: Author
    content: str
    timestamp: str
    group_openid: str
    attachments: Optional[List[Attachment]] = None


class SendMessageRequest(BaseModel):
    content: Optional[str] = None
    msg_type: int = 0
    msg_id: Optional[str] = None
    msg_seq: Optional[int] = None
    event_id: Optional[str] = None


class SendMessageResponse(BaseModel):
    id: str
    timestamp: int
