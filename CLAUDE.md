# Vinha Digital

NiceGUI web app with Google OAuth and SQLite database.

## Tech Stack

- **UI**: NiceGUI (built on FastAPI/Starlette)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migrations**: Alembic
- **Auth**: Authlib (Google OAuth via OIDC)
- **i18n**: python-i18n (JSON locale files, fallback to English)
- **Runtime**: Python 3.14, managed by uv
- **Build**: hatchling (src layout)

## Project Structure

- `src/vinha/main.py` - App entry point, middleware registration, `ui.run()`
- `src/vinha/auth.py` - OAuth config, login/callback/logout routes, AuthMiddleware
- `src/vinha/db.py` - SQLModel engine and session factory
- `src/vinha/models.py` - SQLModel table models
- `src/vinha/pages/` - NiceGUI page handlers (one file per page)
- `src/vinha/locales/` - i18n translation files (`en.json`, `pt.json`)
- `alembic/` - Migration scripts (auto-generated, `env.py` imports SQLModel metadata)

## Commands

```bash
uv run vinha                                                # Run the app (entry point)
uv run alembic upgrade head                                 # Apply all migrations
uv run alembic revision --autogenerate -m "description"     # Generate migration from model changes
uv run alembic downgrade -1                                 # Roll back one migration
```

## Conventions

- All database models go in `src/vinha/models.py` using SQLModel with `table=True`
- New pages go in `src/vinha/pages/` and must be imported in `main.py`
- OAuth routes are plain FastAPI routes in `auth.py` (not NiceGUI pages)
- Auth state lives in Starlette `request.session` (set by SessionMiddleware)
- NiceGUI pages accept `request: Request` param to read session data
- Use absolute imports with `vinha.` prefix (e.g. `from vinha.models import User`)
- Translations use `t(key, **kwargs)` via python-i18n; locale files live in `src/vinha/locales/`
- User language is auto-detected from `Accept-Language` on first login, switchable from the home page
- Environment secrets loaded from `.env` via python-dotenv
- Never commit `.env` or `vinha.db`
