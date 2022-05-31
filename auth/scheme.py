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


class Wishlist(BaseModel):
    liked_housing_id: int


class CreateWishlist(BaseModel):
    housing_id: int


class DeleteWishlist(BaseModel):
    housing_id: Optional[int]
    liked_housing_id: Optional[int]


class Profile(User):
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = None
    birth_date: Optional[datetime.date] = None
