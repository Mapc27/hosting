from typing import Optional

from pydantic import BaseModel


class ChatCreate(BaseModel):
    user_id: int


class CategoryCreate(BaseModel):
    name: str
    description: str
    level: int


class HousingTypeCreate(BaseModel):
    name: str
    description: str


class HouseCreate(BaseModel):
    name: str
    address: str
    description: str
