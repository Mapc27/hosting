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


class HouseCreate(BaseModel):
    name: str
    address: str
    description: str


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
