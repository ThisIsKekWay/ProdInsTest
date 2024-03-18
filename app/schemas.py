from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date


class SUserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SChangeState(BaseModel):
    param: str
    email: EmailStr


class SAdvList(BaseModel):
    limit: int
    offset: int


class SAdvCreate(BaseModel):
    title: str
    description: str


class SDelete(BaseModel):
    type: str
    id: int