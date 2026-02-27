from fastapi import Request
from nicegui import ui

from vinha.i18n import set_locale, t


@ui.page("/login")
def login_page(request: Request):
    set_locale(request.session.get("language", "en"))
    redirect = request.query_params.get("redirect", "/")

    with ui.column().classes("absolute-center items-center gap-4"):
        ui.label(t("app_name")).classes("text-h4 text-weight-bold")
        ui.button(
            t("sign_in_with_google"),
            on_click=lambda: ui.navigate.to(f"/auth/login?redirect={redirect}"),
        ).classes("q-px-xl")
