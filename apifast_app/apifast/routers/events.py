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
        # Send an initial keep-alive message to establish the connection
        yield ": keep-alive\n\n"

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
                data = json.dumps(data.decode())

                yield f"data: {data}\n\n"

            await asyncio.sleep(0.01)

    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.aclose()


router = APIRouter()


@router.get("/events/character/{channel}")
async def sse(channel: str, request: Request):
    return StreamingResponse(
        sse_event_stream(request, channel),
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
