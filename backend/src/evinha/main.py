from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from evinha.admin.router import router as admin_router
from evinha.auth.router import router as auth_router
from evinha.fundraisers.router import router as fundraisers_router
from evinha.config import IS_CLOUD, settings
from evinha.firebase import init_firebase

init_firebase()

app = FastAPI(title="e-Vinha API")

if not IS_CLOUD:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(fundraisers_router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
