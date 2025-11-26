from dataclasses import dataclass

import msgpack
import redis.asyncio as redis
from fastapi import APIRouter, Depends, Request
from fastmcp import Client
from google import genai
from google.genai import types as genai_types
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
    redis: redis.Redis = Depends(get_redis),
) -> ServerMessage | None:
    try:
        async with mcp_client:
            packed = await redis.get("chat:1:history")
            if packed:
                history = msgpack.unpackb(packed, raw=False)
            else:
                history = []
            chat: AsyncChat = client.aio.chats.create(
                model="gemini-2.5-flash",
                config=genai_types.GenerateContentConfig(
                    system_instruction="""You are a helpful assistant. You have access to tools for looking up specific character details. 
                                      However, for general questions (like history, fashion, culture), answer directly using your internal 
                                      knowledge.""",
                    tools=[mcp_client.session],
                    tool_config=genai_types.ToolConfig(
                        function_calling_config=genai_types.FunctionCallingConfig(
                            mode="AUTO"
                        )
                    ),
                ),
                history=[genai_types.Content(**item) for item in history],
            )
            response = await chat.send_message(message.content)
            if response:
                history_to_save = [item.model_dump() for item in chat.get_history()]
                packed = msgpack.packb(history_to_save, use_bin_type=True)
                await redis.set("chat:1:history", packed)
                if response.text:
                    return ServerMessage(assistant=response.text)
    except Exception as e:
        print(e)
