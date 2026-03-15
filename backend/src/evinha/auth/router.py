from fastapi import APIRouter, Cookie, HTTPException, Response
from firebase_admin import auth as firebase_auth
from pydantic import BaseModel

from evinha.users.repository import upsert_user_on_login

from .jwt import COOKIE_NAME, clear_auth_cookie, create_token, decode_token, set_auth_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


class FirebaseLoginRequest(BaseModel):
    id_token: str


@router.post("/firebase")
async def login_firebase(body: FirebaseLoginRequest) -> Response:
    try:
        decoded = firebase_auth.verify_id_token(body.id_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    user_record = await upsert_user_on_login(
        email=decoded["email"],
        name=decoded.get("name", ""),
        picture=decoded.get("picture", ""),
    )
    token = create_token({
        "email": user_record["email"],
        "name": user_record["name"],
        "picture": user_record["picture"],
        "is_admin": user_record["is_admin"],
        "sections": user_record["sections"],
    })
    response = Response(status_code=200)
    set_auth_cookie(response, token)
    return response


@router.get("/me")
async def get_current_user(
    evinha_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    if not evinha_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(evinha_session)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {
        "email": payload["email"],
        "name": payload["name"],
        "picture": payload["picture"],
        "is_admin": payload.get("is_admin", False),
        "sections": payload.get("sections", {}),
    }


@router.post("/logout")
async def logout() -> Response:
    response = Response(status_code=200)
    clear_auth_cookie(response)
    return response
