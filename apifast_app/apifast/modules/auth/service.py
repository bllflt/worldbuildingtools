from typing import Annotated

import jwt
from apifast.config import config
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer

cookie_auth_scheme = APIKeyCookie(name="access_token", auto_error=False)
token_auth_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    token: Annotated[
        HTTPAuthorizationCredentials | None, Depends(token_auth_scheme)
    ] = None,
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
