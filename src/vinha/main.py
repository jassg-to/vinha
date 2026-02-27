import os

from dotenv import load_dotenv

load_dotenv()

from nicegui import app, ui  # noqa: E402
from starlette.middleware.sessions import SessionMiddleware  # noqa: E402

import vinha.pages.home  # noqa: E402, F401
import vinha.pages.login  # noqa: E402, F401
from vinha.auth import AuthMiddleware, auth_callback, login, logout  # noqa: E402

app.add_route("/auth/login", login, methods=["GET"])
app.add_route("/auth/callback", auth_callback, methods=["GET"], name="auth_callback")
app.add_route("/auth/logout", logout, methods=["GET"])

app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=os.environ["STORAGE_SECRET"])


def main():
    ui.run(title="Vinha", port=8080, reload=True, storage_secret=os.environ["STORAGE_SECRET"])


if __name__ in {"__main__", "__mp_main__"}:
    main()
