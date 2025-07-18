from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from src.database.models import UserRole

PhoneNumber.phone_format = "E164"


class ContactModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=256)
    phone: PhoneNumber
    birthday: date
    note: Optional[str] = None


class ContactResponse(ContactModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr


class RequestPassword(BaseModel):
    password: str
