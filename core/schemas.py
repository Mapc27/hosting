from typing import Optional, List, Dict, Union

from pydantic import BaseModel


class ChatCreate(BaseModel):
    user_id: int


class ChatDelete(BaseModel):
    chat_id: int


class CategoryCreate(BaseModel):
    name: str
    description: str
    level: int


class HousingTypeCreate(BaseModel):
    name: str
    description: str


class Characteristic(BaseModel):
    characteristic_id: int
    amount: int


class HouseCreate(BaseModel):
    name: str
    address: str
    description: str
    characteristics: List[Characteristic]
    category_id: int
    type_id: int
    per_night: int


class HouseChange(BaseModel):
    name: Union[str, None] = None
    address: Union[str, None] = None
    description: Union[str, None] = None
    characteristics: Union[List[Characteristic], None] = None
    category_id: Union[int, None] = None
    type_id: Union[int, None] = None
    per_night: Union[int, None] = None


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
