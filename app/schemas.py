from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AdvertisementResponse(BaseModel):
    title: str
    price: float
    model: str
    marka: str
    region: str
    mileage: str
    color: str
    contact_info: Optional[str]  # Обновлено
    link: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
        

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

    class Config:
        orm_mode = True


