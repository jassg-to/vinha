from authlib.integrations.httpx_client import AsyncOAuth2Client

from evinha.config import settings

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def _create_client() -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=f"{settings.BACKEND_URL}/auth/callback",
        scope="openid email profile",
    )


def get_authorization_url() -> str:
    client = _create_client()
    url, _state = client.create_authorization_url(AUTHORIZE_URL)
    return url


async def exchange_code(code: str) -> dict:
    client = _create_client()
    async with client:
        token = await client.fetch_token(TOKEN_URL, code=code)  # noqa: F841
        resp = await client.get(USERINFO_URL)
        resp.raise_for_status()
        info = resp.json()
    return {
        "email": info["email"],
        "name": info.get("name", ""),
        "picture": info.get("picture", ""),
    }
