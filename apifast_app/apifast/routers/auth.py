from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from apifast.config import config


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter()
cookie_auth_scheme = APIKeyCookie(name="access_token", auto_error=False)
token_auth_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(token_auth_scheme)] = None,
    cookie: Annotated[str | None, Depends(cookie_auth_scheme)] = None,
) -> str:
    
    actual_token = token.credentials if token else cookie
    
    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication cookie",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(actual_token, config.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


@router.post("/auth/login")
async def login(request: LoginRequest, response: Response) -> dict[str, str]:
    payload = {
        "sub": request.username,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=config.jwt_token_ttl),  # datetime.utcnow() is deprecated
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm="HS256")

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none",
        secure=False,
        expires=3600,
        path="/",
    )

    return {"message": "Login successful"}


@router.get("/auth/me")
async def me(current_user: str = Depends(get_current_user)) -> dict[str, str]:
    return {"username": current_user, "authenticated": "true"}


@router.post("/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token", path="/")
    return {"message": "Logout successful"}
