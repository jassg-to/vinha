from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.async_client import AsyncClient
from google.oauth2 import service_account

from evinha.config import settings

_db: AsyncClient | None = None
_sa_path: Path | None = None


def init_firebase() -> None:
    global _sa_path
    path = Path(settings.FIREBASE_SERVICE_ACCOUNT)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    _sa_path = path
    cred = credentials.Certificate(str(path))
    firebase_admin.initialize_app(cred)


def get_db() -> AsyncClient:
    global _db
    if _db is None:
        sa_creds = service_account.Credentials.from_service_account_file(str(_sa_path))
        sync_client = firestore.client()
        _db = AsyncClient(project=sync_client.project, credentials=sa_creds)
    return _db
