import os
from datetime import datetime, timezone
from pathlib import Path

import i18n
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlmodel import select
from starlette.middleware.base import BaseHTTPMiddleware

from vinha.db import get_session
from vinha.models import User

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

UNRESTRICTED_PATHS = {"/login", "/auth/login", "/auth/callback"}
UNRESTRICTED_PREFIXES = ("/_nicegui", "/static", "/_next")

i18n.set("load_path", [str(Path(__file__).parent / "locales")])
i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope["path"]

        request.state.translate = Translate(request.session.get("language", "en"))

        if path in UNRESTRICTED_PATHS or any(path.startswith(p) for p in UNRESTRICTED_PREFIXES):
            return await call_next(request)

        if not request.session.get("user"):
            return RedirectResponse(f"/login?redirect={path}")

        return await call_next(request)


class Translate:
    def __init__(self, locale: str):
        self.locale = locale

    def __call__(self, key: str, **kwargs: str) -> str:
        return i18n.t(key, **kwargs)


async def login(request: Request):
    redirect = request.query_params.get("redirect", "/")
    request.session["redirect_after_login"] = redirect
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token["userinfo"]

    with get_session() as session:
        user = session.exec(select(User).where(User.google_sub == userinfo["sub"])).first()
        if user:
            user.last_login = datetime.now(timezone.utc)
            user.name = userinfo.get("name", user.name)
            user.picture = userinfo.get("picture", user.picture)
        else:
            accept_lang = request.headers.get("accept-language", "")
            lang = "pt" if accept_lang.startswith("pt") else "en"
            user = User(
                google_sub=userinfo["sub"],
                email=userinfo["email"],
                name=userinfo.get("name", ""),
                picture=userinfo.get("picture"),
                language=lang,
            )
            session.add(user)
        session.commit()
        language = user.language

    request.session["language"] = language
    request.session["user"] = {
        "email": userinfo["email"],
        "name": userinfo.get("name", ""),
        "picture": userinfo.get("picture", ""),
    }

    redirect = request.session.pop("redirect_after_login", "/")
    return RedirectResponse(redirect)


async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
