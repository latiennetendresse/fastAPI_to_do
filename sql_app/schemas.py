from typing import List, Optional

from pydantic import BaseModel, EmailStr


class TaskBase(BaseModel):
    title: str


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    is_done: bool
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):

    email: str
    name: str


class UserCreate(UserBase):
    email: EmailStr
    name: str
    password: str


class User(UserBase):
    id: int
    # tasks: List[Task] = []

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str