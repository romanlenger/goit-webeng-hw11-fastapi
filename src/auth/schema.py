from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email : EmailStr

class UserCreate(User):
    password: str

class UserResponse(User):
    id: int

    class Config:
        from_attributes = True


