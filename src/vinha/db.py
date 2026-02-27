from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///vinha.db"

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    return Session(engine)
