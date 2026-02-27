from fastapi import Request
from nicegui import ui


@ui.page("/login")
def login_page(request: Request):
    redirect = request.query_params.get("redirect", "/")

    with ui.column().classes("absolute-center items-center gap-4"):
        ui.label("Vinha").classes("text-h4 text-weight-bold")
        ui.button(
            "Sign in with Google",
            on_click=lambda: ui.navigate.to(f"/auth/login?redirect={redirect}"),
        ).classes("q-px-xl")
