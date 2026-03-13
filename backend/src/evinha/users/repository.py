from datetime import datetime, timezone

from google.cloud.firestore import AsyncClient

from evinha.firebase import get_db
from evinha.users.models import ROLES, SECTIONS

COLLECTION = "users"
ALIASES_COLLECTION = "email_aliases"


async def _resolve_email(db: AsyncClient, email: str) -> str:
    """Check if email is an alias and return the primary email."""
    alias_doc = await db.collection(ALIASES_COLLECTION).document(email).get()
    if alias_doc.exists:
        return alias_doc.to_dict()["primary"]
    return email


async def get_user(email: str) -> dict | None:
    db = get_db()
    primary = await _resolve_email(db, email)
    doc = await db.collection(COLLECTION).document(primary).get()
    return doc.to_dict() if doc.exists else None


async def upsert_user_on_login(email: str, name: str, picture: str) -> dict:
    db = get_db()
    primary = await _resolve_email(db, email)
    ref = db.collection(COLLECTION).document(primary)
    doc = await ref.get()
    now = datetime.now(timezone.utc).isoformat()

    if doc.exists:
        await ref.update({"name": name, "picture": picture, "last_login": now})
        updated = await ref.get()
        return updated.to_dict()

    is_first = await _is_collection_empty(db)
    data = {
        "email": email,
        "emails": [email],
        "name": name,
        "picture": picture,
        "is_admin": is_first,
        "sections": {s: "manager" for s in sorted(SECTIONS)} if is_first else {},
        "created_at": now,
        "last_login": now,
    }
    await ref.set(data)
    return data


async def _is_collection_empty(db: AsyncClient) -> bool:
    docs = db.collection(COLLECTION).limit(1).stream()
    async for _ in docs:
        return False
    return True


async def list_users() -> list[dict]:
    db = get_db()
    docs = db.collection(COLLECTION).stream()
    return [doc.to_dict() async for doc in docs]


async def update_user_permissions(
    email: str, is_admin: bool, sections: dict[str, str]
) -> dict | None:
    invalid_sections = set(sections.keys()) - SECTIONS
    if invalid_sections:
        raise ValueError(f"Invalid sections: {invalid_sections}")

    invalid_roles = {r for r in sections.values() if r not in ROLES}
    if invalid_roles:
        raise ValueError(f"Invalid roles: {invalid_roles}")

    db = get_db()
    ref = db.collection(COLLECTION).document(email)
    doc = await ref.get()
    if not doc.exists:
        return None

    await ref.update({"is_admin": is_admin, "sections": sections})
    updated = await ref.get()
    return updated.to_dict()


async def merge_users(primary_email: str, secondary_email: str) -> dict:
    """Merge secondary user into primary. Keeps primary's permissions.
    Secondary user doc is deleted; secondary email becomes an alias."""
    if primary_email == secondary_email:
        raise ValueError("Cannot merge a user with themselves")

    db = get_db()

    primary_ref = db.collection(COLLECTION).document(primary_email)
    primary_doc = await primary_ref.get()
    if not primary_doc.exists:
        raise ValueError(f"Primary user not found: {primary_email}")

    secondary_ref = db.collection(COLLECTION).document(secondary_email)
    secondary_doc = await secondary_ref.get()
    if not secondary_doc.exists:
        raise ValueError(f"Secondary user not found: {secondary_email}")

    primary_data = primary_doc.to_dict()
    secondary_data = secondary_doc.to_dict()

    # Collect all emails from both users
    all_emails = list(dict.fromkeys(
        primary_data.get("emails", [primary_email])
        + secondary_data.get("emails", [secondary_email])
    ))

    # Update primary with merged email list
    await primary_ref.update({"emails": all_emails})

    # Create alias entries for all secondary emails
    for email in secondary_data.get("emails", [secondary_email]):
        if email != primary_email:
            await db.collection(ALIASES_COLLECTION).document(email).set(
                {"primary": primary_email}
            )

    # Delete secondary user doc
    await secondary_ref.delete()

    updated = await primary_ref.get()
    return updated.to_dict()
