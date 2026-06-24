import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from charservice.auth.jwt import create_access_token
from charservice.config import config
from charservice.db import get_db
from charservice.modules.auth.models import User
from charservice.modules.auth.schemas import LoginRequest
from charservice.modules.auth.service import get_current_user

router = APIRouter()


@router.post("/auth/login")
async def login(
    request: LoginRequest, response: Response, session: Session = Depends(get_db)
) -> dict[str, str]:

    user: User | None = session.exec(
        select(User).where(User.username == request.username)
    ).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nope")
    if not user.verify_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nope")

    response.set_cookie(
        key="access_token",
        value=create_access_token({"sub": f"user_id:{user.id}"}),
        httponly=True,
        samesite="none",
        secure=False,
        expires=config.cookie_expire,
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


@router.get("/auth/check")
async def check_auth(current_user: str = Depends(get_current_user)) -> Response:
    """
    Endpoint for Nginx auth_request.
    Returns 200 if authenticated, otherwise get_current_user raises 401.
    Sets
        X-User-ID
        X-Permitted-Stories
    """

    current_user_id = int(current_user[8:])  # Strip "user_id:" prefix

    url = "http://localhost:2000/api/v1/get_permitted_stories"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"user_id": current_user_id},
                timeout=3.0,
            )
            print(response)
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        print(client.request)
        raise

    return Response(
        status_code=status.HTTP_200_OK,
        headers={
            "X-User-ID": str(current_user_id),
            "X-Permitted-Stories": ",".join(map(str, response.json())),
        },
    )
