from dataclasses import dataclass

import httpx
from fastapi import APIRouter, Request

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
    request=Request,
) -> ServerMessage | None:
    try:
        url = f"{config.llm_proxy_url}/api/v1/chat/message"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json={"user_id": 1, "message": message.content}, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return ServerMessage(assistant=data["assistant"])
    except Exception:
        return None
