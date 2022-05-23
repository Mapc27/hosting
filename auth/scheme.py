import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    expires: datetime.datetime


class BaseUser(BaseModel):
    email: str


class User(BaseUser):
    name: Optional[str] = None
    surname: Optional[str] = None


class UserCreate(BaseUser):
    password: str
    email: str


class Login(BaseModel):
    email: str
    password: str
