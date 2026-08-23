"""Neon-backed signup and signin endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignupRequest(BaseModel):   #BaseModel is used to create a data model/schema.
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=320)
    # Bcrypt accepts at most 72 UTF-8 bytes, so enforce that limit at the API.
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")  #tells pydentic to Run this function whenever you validate the password field.
    @classmethod
    def validate_password_bytes(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 UTF-8 bytes or shorter")
        return password


class SigninRequest(BaseModel):
    # A user may sign in with either their username or email address.
    login: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=72)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _normalise_identity(value: str) -> str:
    """Make email/username comparisons consistent regardless of user casing."""
    return value.strip().lower()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED, #status provides readable names for HTTP status codes
)
def signup(request: SignupRequest, db: Session = Depends(get_db)): #Depends = "FastAPI, give me this required thing/function.
    username = _normalise_identity(request.username)
    email = _normalise_identity(request.email)

    if "@" not in email:
        raise HTTPException(status_code=422, detail="Enter a valid email address")

    # Check both unique fields first to return a friendly error before insert.
    existing_user = db.scalar(
        select(User).where(or_(User.username == username, User.email == email))
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        )

    user = User(
        username=username,
        email=email,
        # Only the password hash is saved to Neon; never save plain passwords.
        password_hash=hash_password(request.password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)  # Loads database-generated values, including the UUID.
    except IntegrityError as exc:
        # The database constraint still protects against two simultaneous signups.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        ) from exc

    return user


@router.post("/signin", response_model=TokenResponse)
def signin(request: SigninRequest, db: Session = Depends(get_db)):
    login = _normalise_identity(request.login)

    user = db.scalar(
        select(User).where(or_(User.username == login, User.email == login))
    )

    # Use one generic response so callers cannot discover which accounts exist.
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))
