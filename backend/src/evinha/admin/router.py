from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from evinha.auth.dependencies import require_admin
from evinha.users.models import SECTIONS
from evinha.users.repository import list_users, merge_users, update_user_permissions

router = APIRouter(prefix="/admin", tags=["admin"])


class PermissionsUpdate(BaseModel):
    is_admin: bool
    sections: dict[str, str]  # section_name -> role, omit section to remove access


class MergeRequest(BaseModel):
    primary_email: str
    secondary_email: str


@router.get("/users")
async def get_users(caller: dict = Depends(require_admin)) -> list[dict]:
    return await list_users()


@router.patch("/users/{email}/permissions")
async def patch_user_permissions(
    email: str,
    body: PermissionsUpdate,
    caller: dict = Depends(require_admin),
) -> dict:
    if email == caller["email"] and not body.is_admin:
        raise HTTPException(
            status_code=400, detail="Cannot remove your own admin status"
        )
    try:
        result = await update_user_permissions(email, body.is_admin, body.sections)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.post("/users/merge")
async def post_merge_users(
    body: MergeRequest,
    caller: dict = Depends(require_admin),
) -> dict:
    try:
        return await merge_users(body.primary_email, body.secondary_email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sections")
async def get_sections(caller: dict = Depends(require_admin)) -> list[str]:
    return sorted(SECTIONS)
