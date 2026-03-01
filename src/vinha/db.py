import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///vinha.db")

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    return Session(engine)
