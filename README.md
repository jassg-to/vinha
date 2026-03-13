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

3. Install and run the backend:

   ```bash
   cd backend
   uv sync
   uv run uvicorn evinha.main:app --port 8080 --reload
   ```

4. In a separate terminal, install and run the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Open http://localhost:5173 in your browser.

## License

[Affero General Public License 3.0](LICENSE)
