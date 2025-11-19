import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from apifast.mdb import get_redis

redis_client = get_redis()


async def sse_event_stream(request: Request, channel_name: str, keepalive_interval=15):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)

    try:
        last_keepalive = 0
        while True:
            if await request.is_disconnected():
                break

            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            now = asyncio.get_event_loop().time()

            if now - last_keepalive > keepalive_interval:
                yield ": keep-alive\n\n"
                last_keepalive = now

            if message:
                data = message["data"]

                #
                if not isinstance(data, str):
                    data = json.dumps(data)

                yield f"data: {data}\n\n"


            await asyncio.sleep(0.01)

    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()


router = APIRouter()


@router.get("/events/{channel}")
async def sse(channel: str, request: Request):
    return StreamingResponse(
        sse_event_stream(request, channel), media_type="text/event-stream"
    )
