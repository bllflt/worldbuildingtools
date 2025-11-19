from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from apifast.mcp.characters import mcp as mcp_characters
from apifast.routers import (
    ai,
    character_connections,
    characters,
    events,
    images,
    partnership_participants,
    partnerships,
)

mcp = FastMCP("My App MCP")
mcp_app = mcp.http_app("/")


@asynccontextmanager
async def app_lifespan(_fastapi_app: FastAPI):
    await mcp.import_server(mcp_characters, prefix="characters")
    yield


@asynccontextmanager
async def combined_lifespan(fastapi_app: FastAPI):
    async with app_lifespan(fastapi_app):
        async with mcp_app.lifespan(fastapi_app):
            yield


app = FastAPI(lifespan=combined_lifespan)
app.mount("/mcp", mcp_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # MCP SuperAssistant requires this, MCP Inspector does not
    # expose_headers=["mcp-session-id"],
)

app.include_router(characters.router, prefix="/api/v1")
app.include_router(character_connections.router, prefix="/api/v1")
app.include_router(partnerships.router, prefix="/api/v1")
app.include_router(partnership_participants.router, prefix="/api/v1")

app.include_router(ai.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")

app.include_router(images.router)
