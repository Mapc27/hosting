from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    name: Optional[str] = None
    surname: Optional[str] = None
    disabled: Optional[bool] = None


class UserCreate(User):
    password: str


class Login(BaseModel):
    email: str
    password: str


class UserInDB(User):
    hashed_password: str
