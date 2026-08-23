import os

from dotenv import load_dotenv

load_dotenv()


def _sqlalchemy_database_url(url: str | None) -> str | None:
    """Use the installed Psycopg 3 driver for Neon/PostgreSQL URLs."""
    if not url:
        return None
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _sqlalchemy_database_url(os.getenv("DATABASE_URL"))
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
