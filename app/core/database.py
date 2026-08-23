from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


_session_factory = None


def get_session_factory():
    """Create a database connection pool only when a database route uses it."""
    global _session_factory

    if _session_factory is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")

        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        _session_factory = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )

    return _session_factory


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
