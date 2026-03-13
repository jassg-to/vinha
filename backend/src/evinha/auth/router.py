from fastapi import APIRouter, Cookie, Response
from fastapi.responses import RedirectResponse

from evinha.config import settings

from .google import exchange_code, get_authorization_url
from .jwt import COOKIE_NAME, clear_auth_cookie, create_token, decode_token, set_auth_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def login_google() -> RedirectResponse:
    url = get_authorization_url()
    return RedirectResponse(url)


@router.get("/callback")
async def auth_callback(code: str) -> RedirectResponse:
    user_info = await exchange_code(code)
    token = create_token(user_info)
    response = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)
    set_auth_cookie(response, token)
    return response


@router.get("/me")
async def get_current_user(
    evinha_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    if not evinha_session:
        return Response(status_code=401)
    payload = decode_token(evinha_session)
    if not payload:
        return Response(status_code=401)
    return {
        "email": payload["email"],
        "name": payload["name"],
        "picture": payload["picture"],
    }


@router.post("/logout")
async def logout() -> Response:
    response = Response(status_code=200)
    clear_auth_cookie(response)
    return response
