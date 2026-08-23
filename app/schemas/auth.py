from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=320)
    # Bcrypt accepts at most 72 UTF-8 bytes.
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
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
