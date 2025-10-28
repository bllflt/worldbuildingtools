from apifast.routers import characters
from fastapi import FastAPI

app = FastAPI()
app.include_router(characters.router, prefix='/api/v1')
