import logging
from dataclasses import dataclass

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from charservice.auth.jwt import create_access_token
from charservice.config import config
from charservice.modules.auth.service import get_current_user, get_permitted_stories

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
    story_uuid: str = Query(None, description="story UUID for context"),
    permitted_stories: set[str] = Depends(get_permitted_stories),
    current_user: str = Depends(get_current_user)
) -> ServerMessage | None:
    logging.info(f"Received client message: {message}")

    if story_uuid not in permitted_stories:
        logging.warning(f"Access denied to story {story_uuid}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to story {story_uuid}",
        )

    url = f"{config.llm_proxy_url}/api/v1/chat/message"
    token = create_access_token({"sub": "apifast"})
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "content": message.content,
                    "story_uuid": story_uuid,
                    "user_id": current_user,
                    "permitted_stories": list(permitted_stories),
                },
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
async def get_client_history(current_user: str = Depends(get_current_user)):

    token = create_access_token({"sub": "apifast"})
    url = f"{config.llm_proxy_url}/api/v1/chat/get_history/{current_user}"
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
