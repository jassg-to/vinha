from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from evinha.auth.router import router as auth_router
from evinha.config import settings

app = FastAPI(title="e-Vinha API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
