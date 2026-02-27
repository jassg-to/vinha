from fastapi import Request
from nicegui import ui


@ui.page("/")
def home_page(request: Request):
    user = request.session.get("user", {})

    with ui.column().classes("absolute-center items-center gap-4"):
        if user.get("picture"):
            ui.image(user["picture"]).classes("w-24 h-24 rounded-full")
        ui.label(f"Welcome, {user.get('name', 'User')}").classes("text-h5")
        ui.label(user.get("email", "")).classes("text-subtitle1 text-grey")
        ui.button("Logout", on_click=lambda: ui.navigate.to("/auth/logout")).props("outline")
