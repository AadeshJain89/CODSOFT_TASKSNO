from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re


# ---------------------- User Schemas ----------------------

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for login and profile")
    email: EmailStr = Field(..., description="Valid email address")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="User password (min 6 chars)")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserPublic(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# --------------------- Contact Schemas ---------------------

class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Contact first name")
    last_name: Optional[str] = Field(None, max_length=50, description="Contact last name")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=500, description="Contact physical address")
    company: Optional[str] = Field(None, max_length=100, description="Company / Organization name")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            cleaned = v.strip()
            if not re.match(r"^\+?[0-9\s\-\(\)]{7,20}$", cleaned):
                raise ValueError("Invalid phone number format. Must contain 7 to 20 digits, spaces, hyphens, +, ()")
            return cleaned
        return None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=100)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            cleaned = v.strip()
            if not re.match(r"^\+?[0-9\s\-\(\)]{7,20}$", cleaned):
                raise ValueError("Invalid phone number format. Must contain 7 to 20 digits, spaces, hyphens, +, ()")
            return cleaned
        return None


class ContactResponse(ContactBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    total: int
    items: List[ContactResponse]
    skip: int
    limit: int
