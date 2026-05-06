import logging
from dataclasses import dataclass

import httpx
from fastapi import APIRouter

from apifast.auth.jwt import create_access_token
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

    url = f"{config.llm_proxy_url}/api/v1/chat/message"
    token = create_access_token({"sub": "apifast"})
    try:
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


@router.post("/chat/get_history")
async def get_client_history():

    token = create_access_token({"sub": "apifast"})
    url = f"{config.llm_proxy_url}/api/v1/chat/get_history"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    except Exception:
        return None
