from datetime import datetime, timedelta, timezone

from fastapi import Response
import jwt
from jwt.exceptions import PyJWTError

from evinha.config import settings

ALGORITHM = "HS256"
COOKIE_NAME = "evinha_session"
MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def create_token(data: dict) -> str:
    payload = {
        **data,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=MAX_AGE),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except PyJWTError:
        return None


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set True in production behind HTTPS
        path="/",
        max_age=MAX_AGE,
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")
