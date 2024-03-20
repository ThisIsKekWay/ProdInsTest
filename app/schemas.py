from typing import List

from pydantic import BaseModel, EmailStr


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


class SObjListUnfiltered(BaseModel):
    page: int
    page_size: int


class SObjListFiltered(BaseModel):
    category_id: int
    page: int
    page_size: int


class SAdvCreate(BaseModel):
    category_id: int
    title: str
    description: str


class SDelete(BaseModel):
    type: str
    id: int


class SCreateCategory(BaseModel):
    name: str


class SMoveCategory(BaseModel):
    adv_id: int
    target_cat: int

    class Config:
        from_attributes = True


class SReport(BaseModel):
    adv_id: int
    title: str
    content: str


class SAdvDelete(BaseModel):
    id: int


class SGetItem(BaseModel):
    id: int


class SAdvComment(BaseModel):
    advertisement_id: int
    content: str


class SCommentsPag(BaseModel):
    advertisement_id: int
    page: int
    page_size: int


class SEmailUsage(BaseModel):
    emails: List[EmailStr]


class SUserEmails(BaseModel):
    email: EmailStr
