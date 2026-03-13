from fastapi import Cookie, HTTPException

from evinha.users.models import ROLES

from .jwt import COOKIE_NAME, decode_token


async def get_current_user_payload(
    evinha_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    if not evinha_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(evinha_session)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


async def require_admin(
    evinha_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    payload = await get_current_user_payload(evinha_session)
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def require_section(section: str, min_role: str = "viewer"):
    async def dependency(
        evinha_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
    ) -> dict:
        payload = await get_current_user_payload(evinha_session)
        if payload.get("is_admin"):
            return payload
        user_role = payload.get("sections", {}).get(section)
        if not user_role or ROLES.index(user_role) < ROLES.index(min_role):
            raise HTTPException(
                status_code=403,
                detail=f"Requires {min_role} access to {section}",
            )
        return payload

    return dependency
