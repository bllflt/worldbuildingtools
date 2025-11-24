from dataclasses import dataclass

from fastapi import APIRouter, Depends, Request
from fastmcp import Client
from google import genai
from google.genai import types  # noqa: F401
from google.genai.chats import AsyncChat

from apifast.config import config
from apifast.mdb import get_redis

mcp_client = Client("http://127.0.0.1:5000/mcp")
client = genai.Client(api_key=config.gemini_api_key)


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
    redis=Depends(get_redis),
) -> ServerMessage | None:
    try:
        async with mcp_client:
            chat: AsyncChat = client.aio.chats.create(
                model="gemini-2.5-flash",
                config=genai.types.GenerateContentConfig(
                    tools=[mcp_client.session],
                ),
            )
            while True:
                # if await request.is_disconnected():
                #    break
                # if not message.content:
                #     continue
                response = await chat.send_message(message.content)
                if response:
                    return ServerMessage(
                        assistant="".join(
                            part.text for part in response.parts if part.text
                        )
                    )
    except Exception as e:
        print(e)
