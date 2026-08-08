from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from typing import Literal
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value):
        if value is None:
            return None
        return value.lower()


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str = Field(min_length=1, max_length=50)

class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=120)

    


class Token(BaseModel):
    access_token: str
    token_type : str


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    completed: bool
    priority: Literal["low","medium","high"]
    due_date: datetime | None = None
    category: str | None = Field(default=None, max_length=50)
    
class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1)
    completed: bool | None = Field(default=None)
    priority: Literal["low","medium","high"] | None = Field(default=None)
    due_date: datetime | None = None
    category: str | None = Field(default=None, max_length=50)


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int 
    user_id: int
    created_at: datetime
    creator: UserPublic