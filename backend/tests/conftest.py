import pytest
from httpx import ASGITransport, AsyncClient

from tests.fake_firestore import FakeFirestore

fake_db = FakeFirestore()


@pytest.fixture(autouse=True)
def _clean_db():
    fake_db.clear()
    yield
    fake_db.clear()


# Patch get_db before importing the app
import evinha.firebase  # noqa: E402

evinha.firebase.get_db = lambda: fake_db  # type: ignore[assignment]

# Patch firebase init to be a no-op
evinha.firebase.init_firebase = lambda: None  # type: ignore[assignment]

from evinha.main import app  # noqa: E402

from evinha.auth.jwt import COOKIE_NAME, create_token  # noqa: E402


def _make_cookies(email: str = "test@example.com", is_admin: bool = False, sections: dict | None = None):
    payload = {
        "email": email,
        "name": "Test User",
        "picture": "",
        "is_admin": is_admin,
        "sections": sections or {},
    }
    token = create_token(payload)
    return {COOKIE_NAME: token}


def _make_client(cookies: dict) -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test", cookies=cookies)


@pytest.fixture
async def client():
    async with _make_client(_make_cookies(is_admin=True)) as c:
        yield c


@pytest.fixture
async def admin_client():
    async with _make_client(_make_cookies(is_admin=True)) as c:
        yield c


@pytest.fixture
async def manager_client():
    async with _make_client(_make_cookies(sections={"fundraisers": "manager"})) as c:
        yield c


@pytest.fixture
async def editor_client():
    async with _make_client(_make_cookies(sections={"fundraisers": "editor"})) as c:
        yield c


@pytest.fixture
async def viewer_client():
    async with _make_client(_make_cookies(sections={"fundraisers": "viewer"})) as c:
        yield c


@pytest.fixture
async def no_access_client():
    async with _make_client(_make_cookies(sections={})) as c:
        yield c
