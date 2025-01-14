from pydantic import BaseModel, EmailStr
from enum import Enum


class User(BaseModel):
    username: str
    email : EmailStr


class UserCreate(User):
    password: str


class UserResponse(User):
    id: int

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER = "super"
