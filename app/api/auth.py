"""Neon-backed signup and signin endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import SigninRequest, SignupRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
