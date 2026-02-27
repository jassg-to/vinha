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

## Development

```bash
# Create a new migration after changing models
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1
```
