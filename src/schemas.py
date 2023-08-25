from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ContactSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    created_date: Optional[date]

    def __init__(self, **data):
        super().__init__(**data)
        self.created_date = date.today()


class ContactUpdateSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    update_date: Optional[date]

    def __init__(self, **data):
        super().__init__(**data)
        self.update_date = date.today()


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    created_date: datetime | None
    update_date: datetime | None
    user: UserResponseSchema | None

    class Config:
        from_attributes = True


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        from_attributes = True