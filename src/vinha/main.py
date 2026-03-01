import os

from dotenv import load_dotenv

load_dotenv()

from nicegui import app, ui  # noqa: E402
from starlette.middleware.sessions import SessionMiddleware  # noqa: E402
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware  # noqa: E402

import vinha.pages.home  # noqa: E402, F401
import vinha.pages.login  # noqa: E402, F401
from vinha.auth import AuthMiddleware, auth_callback, login, logout  # noqa: E402

app.add_route("/auth/login", login, methods=["GET"])
app.add_route("/auth/callback", auth_callback, methods=["GET"], name="auth_callback")
app.add_route("/auth/logout", logout, methods=["GET"])

app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=os.environ["STORAGE_SECRET"])
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")


def main():
    port = int(os.environ.get("PORT", "8080"))
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    ui.run(
        title="Vinha",
        host="0.0.0.0",
        port=port,
        reload=reload,
        show=False,
        storage_secret=os.environ["STORAGE_SECRET"],
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
