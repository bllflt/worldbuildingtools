from apifast.auth.jwt import create_access_token
from apifast.config import config
from apifast.db import get_db
from apifast.modules.auth.models import User
from apifast.modules.auth.schemas import LoginRequest
from apifast.modules.auth.service import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

router = APIRouter()


@router.post("/auth/login")
async def login(
    request: LoginRequest, response: Response, session: Session = Depends(get_db)
) -> dict[str, str]:

    user: User | None  = session.exec(select(User).where(User.username == request.username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nope"
        )
    if not user.verify_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nope"
        )

    response.set_cookie(
        key="access_token",
        value=create_access_token({"sub": request.username}),
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
    Sets the X-User-ID header for Nginx to forward to backends.
    """
    # In this implementation, current_user is the username from the JWT 'sub'
    return Response(status_code=status.HTTP_200_OK, headers={"X-User-ID": current_user})
