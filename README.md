# e-Vinha

Spiritist Centre operations management web app built for [Joanna de Angelis Spiritist Study Group](https://jassg.ca).

## Prerequisites

- [Node.js](https://nodejs.org/) 22+
- [Python](https://python.org/) 3.14+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A [Firebase](https://firebase.google.com/) project with Firestore enabled (Native mode)

## Setup

1. Clone the repository and copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Fill in your Google OAuth credentials and a random JWT secret in `.env`.

3. Download a Firebase service account key from the Firebase console (Project Settings > Service Accounts > Generate New Private Key) and save it as `backend/service-account.json`. This file is gitignored.

4. Install dependencies:

   ```bash
   cd backend && uv sync
   cd frontend && npm install
   ```

5. Run both dev servers (stops both on Ctrl+C):

   ```powershell
   .\dev.ps1
   ```

   Or run them individually in separate terminals:

   ```bash
   # Backend (port 8080)
   cd backend && uv run uvicorn evinha.main:app --port 8080 --reload

   # Frontend (port 5173)
   cd frontend && npm run dev
   ```

6. Open http://localhost:5173 in your browser. The first user to log in automatically becomes admin.

## Permissions

Users are stored in Firestore. Each user has an admin flag and per-section role assignments. The four sections are: **Library**, **Book Store**, **Fundraisers**, and **Bookings**. Each section supports three role tiers: **Viewer** (read-only), **Editor** (create/modify/delete), and **Manager** (full control). Admins bypass all section checks.

Admins can manage users and assign permissions at `/admin`.

## Internationalization

The UI supports English (en-CA) and Portuguese (pt-BR). The language is auto-detected from your browser settings and can be toggled manually via the language switcher. Translation files are in `frontend/src/lib/i18n/`.

## License

[Affero General Public License 3.0](LICENSE)
