from typing import Optional, List, Dict

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


class Characteristic(BaseModel):
    characteristic: int
    amount: int


class HouseCreate(BaseModel):
    name: str
    address: str
    description: str
    characteristics: List[Characteristic]


class ComfortCategoryCreate(BaseModel):
    name: str


class ComfortCreate(BaseModel):
    name: str


class HousingPricingCreate(BaseModel):
    per_night: int
    cleaning: int
    service: int
    discount_per_week: int
    discount_per_month: int
