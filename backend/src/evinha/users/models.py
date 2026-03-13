from pydantic import BaseModel

SECTIONS = {"library", "book_store", "fundraisers", "bookings"}
ROLES = ("viewer", "editor", "manager")


class UserRecord(BaseModel):
    email: str
    emails: list[str] = []  # all Google emails linked to this user
    name: str
    picture: str
    is_admin: bool = False
    sections: dict[str, str] = {}  # section_name -> role
    created_at: str = ""
    last_login: str = ""
