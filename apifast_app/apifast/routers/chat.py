import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx
import jwt
from fastapi import APIRouter

from apifast.config import config

router = APIRouter()


@dataclass(slots=True)
class ClientMessage:
    content: str


@dataclass(slots=True)
class ServerMessage:
    assistant: str


@router.post("/chat/conversation")
async def get_client_message(
    message: ClientMessage,
) -> ServerMessage | None:
    logging.info(f"Received client message: {message}")

    # Generate JWT token
    payload = {
        "sub": "apifast",
        "exp": datetime.now() + timedelta(hours=1),
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm="HS256")

    try:
        url = f"{config.llm_proxy_url}/api/v1/chat/message"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"content": message.content},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            response.raise_for_status()
            logging.debug(f"LLM proxy response: {response}")
            data = response.json()
            return ServerMessage(assistant=data["assistant"])
    except Exception:
        return None
