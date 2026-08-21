import os
import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


load_dotenv()

security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
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
        