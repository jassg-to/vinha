from fastapi import Request
from nicegui import ui
from sqlmodel import select

from vinha.db import get_session
from vinha.i18n import get_locale, set_locale, t
from vinha.models import User


@ui.page("/")
def home_page(request: Request):
    set_locale(request.session.get("language", "en"))
    user = request.session.get("user", {})

    def switch_language(new_lang: str):
        request.session["language"] = new_lang
        email = user.get("email")
        if email:
            with get_session() as session:
                db_user = session.exec(select(User).where(User.email == email)).first()
                if db_user:
                    db_user.language = new_lang
                    session.commit()
        ui.navigate.to("/")

    with ui.column().classes("absolute-center items-center gap-4"):
        if user.get("picture"):
            ui.image(user["picture"]).classes("w-24 h-24 rounded-full")
        ui.label(t("welcome", name=user.get("name", "User"))).classes("text-h5")
        ui.label(user.get("email", "")).classes("text-subtitle1 text-grey")

        with ui.row().classes("gap-2"):
            ui.button(t("logout"), on_click=lambda: ui.navigate.to("/auth/logout")).props("outline")
            ui.toggle(
                {"en": "EN", "pt": "PT"},
                value=get_locale(),
                on_change=lambda e: switch_language(e.value),
            )
