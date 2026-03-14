# e-Vinha — Spiritist Centre Operations

## Project Layout

Monorepo with a SvelteKit frontend and a FastAPI backend.

```
frontend/   — SvelteKit SPA (Svelte 5, Tailwind v4, adapter-static)
backend/    — FastAPI async API (Python, uv-managed)
```

## Running Dev Servers

Both servers at once (stops both on Ctrl+C):

```powershell
.\dev.ps1
```

Or individually:

```bash
# Backend (port 8080)
cd backend && uv run -m uvicorn evinha.main:app --port 8080 --reload

# Frontend (port 5173)
cd frontend && npm run dev
```

## Key Conventions

- **Svelte 5 runes only**: Use `$state`, `$derived`, `$effect`. Never use the old `$:` reactive syntax.
- **Tailwind CSS v4**: CSS-native config via `@import "tailwindcss"` and `@theme` in `app.css`. No `tailwind.config.js`.
- **Backend deps**: Managed by `uv` via `pyproject.toml`. Never use pip or requirements.txt directly.
- **All backend endpoints are async.**
- **Auth**: Firebase Auth SDK on the frontend (Google sign-in via popup), verified on the backend with `firebase_admin.auth.verify_id_token()`. Session managed via custom JWT in httpOnly cookies. Never use localStorage for auth tokens. Do not use `signInWithRedirect` — it is broken on localhost due to third-party storage partitioning.
- **Database**: Firestore via Firebase Admin SDK (backend only). All Firestore access goes through the FastAPI API — never from the frontend directly. Service account key lives at `backend/service-account.json` (gitignored).
- **Permissions**: Admin flag + per-section roles. Sections: `library`, `book_store`, `fundraisers`, `bookings`. Roles per section: `viewer`, `editor`, `manager` (ordered by privilege). Use `require_admin` or `require_section(section, min_role)` dependencies from `evinha.auth.dependencies` to protect endpoints. Admins bypass all section checks.
- **User data**: Stored in Firestore `users` collection, keyed by email. Upserted on every login. Permissions are embedded in the JWT and take effect on next login after an admin changes them.
- **i18n**: Uses `svelte-i18n`. Translations live in `frontend/src/lib/i18n/{locale}.json`. Wrap all user-facing strings with `$_('key')`. Browser locale is auto-detected; en-CA is the fallback.
    - For Portuguese, do not use gender-hedged structures, just reword to take user gender out of the sentence, e.g. "Boas vindas" instead of "Bem vindo(a)" or "Escrito por" instead of "Autor(a)".
- **License**: AGPL-3.0. The login page includes a link to the source code for compliance.
