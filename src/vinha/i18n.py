from contextvars import ContextVar
from pathlib import Path

import i18n

i18n.set("load_path", [str(Path(__file__).parent / "locales")])
i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")

_current_locale: ContextVar[str] = ContextVar("locale", default="en")


def set_locale(locale: str) -> None:
    _current_locale.set(locale)


def get_locale() -> str:
    return _current_locale.get()


def t(key: str, **kwargs) -> str:
    return i18n.t(key, locale=_current_locale.get(), **kwargs)
