from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apifast.routers import (
    character_connections,
    characters,
    images,
    partnership_participants,
    partnerships,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(characters.router, prefix="/api/v1")
app.include_router(character_connections.router, prefix="/api/v1")
app.include_router(partnerships.router, prefix="/api/v1")
app.include_router(partnership_participants.router, prefix="/api/v1")

app.include_router(images.router)
