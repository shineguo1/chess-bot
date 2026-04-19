import json
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional

from config import settings
from models import (
    WebhookPayload,
    ValidationRequest,
    ValidationResponse,
    C2CMessageEvent,
    GroupAtMessageEvent
)
from signature import SignatureVerifier
from api_client import qq_bot_api
from logger import logger
from command_handler import handle_chess_insight, handle_bind, handle_env, handle_pkm, handle_search, HELP_TEXT
from user_binding import user_binding_storage

signature_verifier = SignatureVerifier(settings.qq_bot_secret)

COMMAND_TIMEOUT = 7.0
ERROR_RETRY_MSG = "⚠️ 命令执行超时或出错，请稍后重试"


async def run_with_timeout(coro, timeout: float = COMMAND_TIMEOUT):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Command timed out after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Command error: {e}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("QQ Bot service starting up...")
    logger.info(f"Bot AppID: {settings.qq_bot_appid}")
    yield
    logger.info("QQ Bot service shutting down...")
    await qq_bot_api.close()


app = FastAPI(
    title="QQ Bot Webhook Service",
    description="QQ机器人Webhook服务 - 响应/insight和/bind命令",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "qq-bot"}


@app.post("/webhook")
async def webhook_handler(
    request: Request,
    x_signature_ed25519: Optional[str] = Header(None, alias="X-Signature-Ed25519"),
    x_signature_timestamp: Optional[str] = Header(None, alias="X-Signature-Timestamp"),
    x_bot_appid: Optional[str] = Header(None, alias="X-Bot-Appid")
):
    body = await request.body()
    body_str = body.decode("utf-8")
    
    logger.info(f"Received webhook request, AppID: {x_bot_appid}")
    logger.debug(f"Request body: {body_str}")
    
    try:
        payload_data = json.loads(body_str)
        payload = WebhookPayload(**payload_data)
    except Exception as e:
        logger.error(f"Failed to parse payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    if payload.op == 13:
        logger.info("Received callback validation request")
        return await handle_validation(payload)
    
    if x_signature_ed25519 and x_signature_timestamp:
        if not signature_verifier.verify_signature(
            x_signature_ed25519, 
            x_signature_timestamp, 
            body_str
        ):
            logger.warning("Signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
        logger.debug("Signature verification passed")
    
    if payload.op == 0 and payload.t:
        is_test = x_bot_appid == "test_app_id" or not x_signature_ed25519
        return await handle_event(payload, is_test=is_test)
    
    return {"status": "ok"}


async def handle_validation(payload: WebhookPayload) -> JSONResponse:
    try:
        validation_data = ValidationRequest(**payload.d)
        signature = signature_verifier.generate_response_signature(
            validation_data.event_ts,
            validation_data.plain_token
        )
        
        response = ValidationResponse(
            plain_token=validation_data.plain_token,
            signature=signature
        )
        
        logger.info(f"Validation response generated for token: {validation_data.plain_token[:8]}...")
        return JSONResponse(content=response.model_dump())
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail="Validation failed")


async def handle_event(payload: WebhookPayload, is_test: bool = False):
    event_type = payload.t
    event_data = payload.d
    
    logger.info(f"Received event: {event_type}")
    
    if event_type == "C2C_MESSAGE_CREATE":
        return await handle_c2c_message(event_data, is_test=is_test)
    elif event_type == "GROUP_AT_MESSAGE_CREATE":
        return await handle_group_message(event_data, is_test=is_test)
    else:
        logger.debug(f"Unhandled event type: {event_type}")
        return {"status": "ignored"}


async def handle_c2c_message(event_data: dict, is_test: bool = False):
    try:
        message = C2CMessageEvent(**event_data)
        content = message.content.strip()
        user_openid = message.author.user_openid
        msg_id = message.id
        
        logger.info(f"C2C message from {user_openid}: {content}")
        
        if content == "/hello":
            if is_test:
                return {"status": "processed", "reply": "hello world"}
            await qq_bot_api.send_c2c_message(
                openid=user_openid,
                content="hello world",
                msg_id=msg_id
            )
            logger.info(f"Replied 'hello world' to user {user_openid}")
        
        elif content == "/help":
            if is_test:
                return {"status": "processed", "reply": HELP_TEXT}
            await qq_bot_api.send_c2c_message(
                openid=user_openid,
                content=HELP_TEXT,
                msg_id=msg_id
            )
            logger.info(f"Replied help to user {user_openid}")
        
        elif content.startswith("/bind"):
            result = await run_with_timeout(handle_bind(content, user_openid))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied bind result to user {user_openid}")
                except Exception as e:
                    logger.error(f"Failed to send bind result: {e}")
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
            else:
                await qq_bot_api.send_c2c_message(
                    openid=user_openid,
                    content=ERROR_RETRY_MSG,
                    msg_id=msg_id
                )
        
        elif content.startswith("/insight"):
            result = await run_with_timeout(handle_chess_insight(content, user_openid))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied insight to user {user_openid}")
                except Exception as e:
                    logger.error(f"Failed to send insight result: {e}")
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
            else:
                await qq_bot_api.send_c2c_message(
                    openid=user_openid,
                    content=ERROR_RETRY_MSG,
                    msg_id=msg_id
                )
        
        elif content.startswith("/env"):
            result = await run_with_timeout(handle_env(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied env to user {user_openid}")
                except Exception as e:
                    logger.error(f"Failed to send env result: {e}")
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
            else:
                await qq_bot_api.send_c2c_message(
                    openid=user_openid,
                    content=ERROR_RETRY_MSG,
                    msg_id=msg_id
                )
        
        elif content.startswith("/pkm"):
            result = await run_with_timeout(handle_pkm(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied pkm to user {user_openid}")
                except Exception as e:
                    logger.error(f"Failed to send pkm result: {e}")
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
            else:
                await qq_bot_api.send_c2c_message(
                    openid=user_openid,
                    content=ERROR_RETRY_MSG,
                    msg_id=msg_id
                )
        
        elif content.startswith("/search"):
            result = await run_with_timeout(handle_search(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied search to user {user_openid}")
                except Exception as e:
                    logger.error(f"Failed to send search result: {e}")
                    await qq_bot_api.send_c2c_message(
                        openid=user_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
            else:
                await qq_bot_api.send_c2c_message(
                    openid=user_openid,
                    content=ERROR_RETRY_MSG,
                    msg_id=msg_id
                )
        
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Failed to handle C2C message: {e}")
        return {"status": "error", "message": str(e)}


async def handle_group_message(event_data: dict, is_test: bool = False):
    try:
        message = GroupAtMessageEvent(**event_data)
        content = message.content.strip()
        group_openid = message.group_openid
        member_openid = message.author.member_openid
        msg_id = message.id
        
        logger.info(f"Group message from group {group_openid}, member {member_openid}: {content}")
        
        if content == "/hello":
            if is_test:
                return {"status": "processed", "reply": "hello world"}
            try:
                await qq_bot_api.send_group_message(
                    group_openid=group_openid,
                    content="hello world",
                    msg_id=msg_id
                )
                logger.info(f"Replied 'hello world' to group {group_openid}")
            except Exception as e:
                logger.error(f"Failed to send hello message: {e}")
        
        elif content == "/help":
            if is_test:
                return {"status": "processed", "reply": HELP_TEXT}
            try:
                await qq_bot_api.send_group_message(
                    group_openid=group_openid,
                    content=HELP_TEXT,
                    msg_id=msg_id
                )
                logger.info(f"Replied help to group {group_openid}")
            except Exception as e:
                logger.error(f"Failed to send help message: {e}")
        
        elif content.startswith("/bind"):
            result = await run_with_timeout(handle_bind(content, member_openid))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied bind result to group {group_openid}")
                except Exception as e:
                    logger.error(f"Failed to send bind message: {e}")
                    try:
                        await qq_bot_api.send_group_message(
                            group_openid=group_openid,
                            content=ERROR_RETRY_MSG,
                            msg_id=msg_id
                        )
                    except:
                        pass
            else:
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
                except:
                    pass
        
        elif content.startswith("/insight"):
            result = await run_with_timeout(handle_chess_insight(content, member_openid))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied insight to group {group_openid}")
                except Exception as e:
                    logger.error(f"Failed to send insight message: {e}")
                    try:
                        await qq_bot_api.send_group_message(
                            group_openid=group_openid,
                            content=ERROR_RETRY_MSG,
                            msg_id=msg_id
                        )
                    except:
                        pass
            else:
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
                except:
                    pass
        
        elif content.startswith("/env"):
            result = await run_with_timeout(handle_env(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied env to group {group_openid}")
                except Exception as e:
                    logger.error(f"Failed to send env message: {e}")
                    try:
                        await qq_bot_api.send_group_message(
                            group_openid=group_openid,
                            content=ERROR_RETRY_MSG,
                            msg_id=msg_id
                        )
                    except:
                        pass
            else:
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
                except:
                    pass
        
        elif content.startswith("/pkm"):
            result = await run_with_timeout(handle_pkm(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied pkm to group {group_openid}")
                except Exception as e:
                    logger.error(f"Failed to send pkm message: {e}")
                    try:
                        await qq_bot_api.send_group_message(
                            group_openid=group_openid,
                            content=ERROR_RETRY_MSG,
                            msg_id=msg_id
                        )
                    except:
                        pass
            else:
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
                except:
                    pass
        
        elif content.startswith("/search"):
            result = await run_with_timeout(handle_search(content))
            if result:
                if is_test:
                    return {"status": "processed", "reply": result}
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=result,
                        msg_id=msg_id
                    )
                    logger.info(f"Replied search to group {group_openid}")
                except Exception as e:
                    logger.error(f"Failed to send search message: {e}")
                    try:
                        await qq_bot_api.send_group_message(
                            group_openid=group_openid,
                            content=ERROR_RETRY_MSG,
                            msg_id=msg_id
                        )
                    except:
                        pass
            else:
                try:
                    await qq_bot_api.send_group_message(
                        group_openid=group_openid,
                        content=ERROR_RETRY_MSG,
                        msg_id=msg_id
                    )
                except:
                    pass
        
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Failed to handle group message: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
