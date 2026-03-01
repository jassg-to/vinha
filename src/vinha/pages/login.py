import configparser
import re
from pathlib import Path

from fastapi import Request
from nicegui import ui

from vinha.auth import Translate


def _get_source_url() -> str:
    """Read the git remote origin URL from .git/config and return a browsable HTTPS URL.

    Raises RuntimeError if the URL cannot be resolved — the server must not start
    without a valid source link (AGPL compliance).
    """
    config = configparser.ConfigParser()
    git_config = Path(".git/config")
    if not config.read(git_config):
        raise RuntimeError(f"AGPL: cannot read {git_config.resolve()}")
    try:
        url = config['remote "origin"']["url"]
    except KeyError:
        raise RuntimeError(f"AGPL: no remote 'origin' in {git_config.resolve()}")
    # Convert SSH URLs: git@host:user/repo.git → https://host/user/repo
    m = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
    if m:
        return f"https://{m.group(1)}/{m.group(2)}"
    return url.removesuffix(".git")


SOURCE_URL: str = _get_source_url()


@ui.page("/login")
def login_page(request: Request):
    t: Translate = request.state.translate
    redirect = request.query_params.get("redirect", "/")

    with ui.column().classes("absolute-center items-center gap-4"):
        ui.label(t("app_name")).classes("text-h4 text-weight-bold")
        ui.button(
            t("sign_in_with_google"),
            on_click=lambda: ui.navigate.to(f"/auth/login?redirect={redirect}"),
        ).classes("q-px-xl")
        ui.link(t("source_code"), SOURCE_URL, new_tab=True).classes("text-caption text-grey-7")
