# e-Vinha — Spiritist Centre Operations

## Project Layout

Monorepo with a SvelteKit frontend and a FastAPI backend.

```
frontend/   — SvelteKit SPA (Svelte 5, Tailwind v4, adapter-static)
backend/    — FastAPI async API (Python, uv-managed)
```

## Running Dev Servers

```bash
# Backend (port 8080)
cd backend && uv run uvicorn evinha.main:app --port 8080 --reload

# Frontend (port 5173)
cd frontend && npm run dev
```

## Key Conventions

- **Svelte 5 runes only**: Use `$state`, `$derived`, `$effect`. Never use the old `$:` reactive syntax.
- **Tailwind CSS v4**: CSS-native config via `@import "tailwindcss"` and `@theme` in `app.css`. No `tailwind.config.js`.
- **Backend deps**: Managed by `uv` via `pyproject.toml`. Never use pip or requirements.txt directly.
- **All backend endpoints are async.**
- **Auth**: JWT tokens stored in httpOnly cookies. Never use localStorage for auth tokens.
- **i18n**: Uses `svelte-i18n`. Translations live in `frontend/src/lib/i18n/{locale}.json`. Wrap all user-facing strings with `$_('key')`. Browser locale is auto-detected; en-CA is the fallback.
    - For Portuguese, do not use gender-hedged structures, just reword to take user gender out of the sentence, e.g. "Boas vindas" instead of "Bem vindo(a)" or "Escrito por" instead of "Autor(a)".
- **License**: AGPL-3.0. The login page includes a link to the source code for compliance.
