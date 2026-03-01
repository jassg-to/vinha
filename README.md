# Vinha Digital

NiceGUI web application with Google OAuth login, backed by SQLite via SQLModel. Supports English and Portuguese (auto-detected, user-switchable).

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Google Cloud OAuth 2.0 credentials

## Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Select **Web application**
6. Add `http://localhost:8080/auth/callback` as an **Authorized redirect URI**
7. Copy the Client ID and Client Secret

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Google OAuth credentials and a random storage secret

# Run database migrations
uv run alembic upgrade head

# Start the app
uv run vinha
```

The app will be available at `http://localhost:8080`.

## Environment Variables

Configured in `.env` (see `.env.example`). Required variables:

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret |
| `STORAGE_SECRET` | Session signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |

Optional (with defaults):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///vinha.db` | Database URL (use absolute path in production) |
| `PORT` | `8080` | Server port |
| `RELOAD` | `false` | Hot-reload for development |

## Development

```bash
# Create a new migration after changing models
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1
```

## Deployment

Each server instance is provisioned with `scripts/setup-instance.sh`, which creates an isolated Linux user, app directory, database directory, and systemd service. The runtime user can only write to the database directory.

```bash
# Provision a new instance (run as root)
curl -fsSL https://raw.githubusercontent.com/jassg-to/vinha/main/scripts/setup-instance.sh | sudo bash -s <instance> <port> https://github.com/jassg-to/vinha.git

# Or from a local clone
sudo ./scripts/setup-instance.sh <instance> <port> https://github.com/jassg-to/vinha.git

# Remove an instance
sudo ./scripts/teardown-instance.sh <instance>
```

Prerequisites: [uv](https://docs.astral.sh/uv/) installed system-wide, a reverse proxy for HTTPS.
