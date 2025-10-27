from fastapi import FastAPI

from apifast.routers import characters

app = FastAPI()
app.include_router(characters.router)
