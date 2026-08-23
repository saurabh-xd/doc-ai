from datetime import datetime, timedelta, timezone

import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET

security = HTTPBearer(auto_error=False)


def _require_jwt_secret() -> str:
    if not JWT_SECRET or len(JWT_SECRET.encode("utf-8")) < 32:
        raise RuntimeError(
            "JWT_SECRET must be set to a random value of at least 32 bytes"
        )
    return JWT_SECRET


def create_access_token(user_id: str) -> str:
    """Helper for the login endpoint you will add later."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": user_id, "exp": expires_at},
        _require_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            _require_jwt_secret(),
            algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "id": user_id
        }

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
