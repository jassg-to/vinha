from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import AsyncClient

from evinha.config import settings

_db: AsyncClient | None = None


def init_firebase() -> None:
    path = Path(settings.FIREBASE_SERVICE_ACCOUNT)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    cred = credentials.Certificate(str(path))
    firebase_admin.initialize_app(cred)


def get_db() -> AsyncClient:
    global _db
    if _db is None:
        _db = firestore.async_client()
    return _db
