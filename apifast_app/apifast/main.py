from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from apifast.mcp.character_connections import mcp as mcp_character_connections
from apifast.mcp.characters import mcp as mcp_characters
from apifast.routers import (
    ai,
    character_connections,
    characters,
    chat,
    events,
    images,
    partnership_participants,
    partnerships,
)

mcp = FastMCP("My App MCP")
mcp.mount(mcp_characters)
mcp.mount(mcp_character_connections)
mcp_app = mcp.http_app("/")

app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # MCP Inspector needs to access the session ID header to correlate requests with MCP sessions
    expose_headers=["mcp-session-id"],
)

app.include_router(characters.router, prefix="/api/v1")
app.include_router(character_connections.router, prefix="/api/v1")
app.include_router(partnerships.router, prefix="/api/v1")
app.include_router(partnership_participants.router, prefix="/api/v1")

app.include_router(ai.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")

app.include_router(chat.router, prefix="/api/v1")

app.include_router(images.router)
