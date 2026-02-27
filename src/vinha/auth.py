import os
from datetime import datetime, timezone

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


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope["path"]

        if path in UNRESTRICTED_PATHS or any(path.startswith(p) for p in UNRESTRICTED_PREFIXES):
            return await call_next(request)

        if not request.session.get("user"):
            return RedirectResponse(f"/login?redirect={path}")

        return await call_next(request)


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
            user = User(
                google_sub=userinfo["sub"],
                email=userinfo["email"],
                name=userinfo.get("name", ""),
                picture=userinfo.get("picture"),
            )
            session.add(user)
        session.commit()

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
