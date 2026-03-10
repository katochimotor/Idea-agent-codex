import sqlite3
from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, create_engine

import backend.models  # noqa: F401
from backend.settings import settings


db_path = Path(settings.database_url.removeprefix("sqlite:///"))
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db() -> None:
    from backend.database.migrations import run_migrations

    run_migrations()


def get_session():
    with Session(engine) as session:
        yield session
