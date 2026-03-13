# e-Vinha

Spiritist Centre operations management web app built for [Joanna de Angelis Spiritist Study Group](https://jassg.ca).

## Prerequisites

- [Node.js](https://nodejs.org/) 22+
- [Python](https://python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup

1. Clone the repository and copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Fill in your Google OAuth credentials and a random JWT secret in `.env`.

3. Install dependencies:

   ```bash
   cd backend && uv sync
   cd frontend && npm install
   ```

4. Run both dev servers (stops both on Ctrl+C):

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

5. Open http://localhost:5173 in your browser.

## Internationalization

The UI supports English (en-CA) and Portuguese (pt-BR). The language is auto-detected from your browser settings and can be toggled manually via the language switcher. Translation files are in `frontend/src/lib/i18n/`.

## License

[Affero General Public License 3.0](LICENSE)
