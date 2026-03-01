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
- `scripts/setup-instance.sh` - Server instance provisioning (users, dirs, systemd, permissions)
- `scripts/teardown-instance.sh` - Removes an instance and all its resources

## Commands

```bash
uv run vinha                                                # Run the app (entry point)
uv run alembic upgrade head                                 # Apply all migrations
uv run alembic revision --autogenerate -m "description"     # Generate migration from model changes
uv run alembic downgrade -1                                 # Roll back one migration
```

## Environment Variables

All read from `.env` via python-dotenv. Only `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `STORAGE_SECRET` are required.

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOOGLE_CLIENT_ID` | (required) | OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | (required) | OAuth 2.0 Client Secret |
| `STORAGE_SECRET` | (required) | Session signing + NiceGUI storage key |
| `DATABASE_URL` | `sqlite:///vinha.db` | SQLAlchemy DB URL (use absolute path in prod) |
| `PORT` | `8080` | Server listen port |
| `RELOAD` | `false` | Hot-reload on file changes (set `true` for local dev) |

## Deployment

Server instances are managed with `scripts/setup-instance.sh` and `scripts/teardown-instance.sh`. Each instance gets:

- A dedicated system user `vinha-<instance>` (no shell, no sudo)
- App code at `/opt/vinha-<instance>/` (read-only for the runtime user)
- Database at `/var/lib/vinha-<instance>/` (sole writable location, enforced by systemd `ProtectSystem=strict`)
- A shared `deploy` user that owns code and can restart services

```bash
# Provision (run as root)
sudo ./scripts/setup-instance.sh prod 8080 https://github.com/jassg-to/vinha.git

# Teardown (run as root)
sudo ./scripts/teardown-instance.sh prod
```

Prerequisites: uv and a reverse proxy installed on the server.

The server at `kiva.gay` is accessed via `ssh claude@kiva.gay` (full sudo).

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
