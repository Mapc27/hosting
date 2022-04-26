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
    name: str
    surname: str
    phone_number: str
    phone_country_code: str
    birth_date: datetime.date


class Login(BaseModel):
    email: str
    password: str
