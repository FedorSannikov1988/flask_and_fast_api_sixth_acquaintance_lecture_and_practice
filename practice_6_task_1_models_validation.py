"""
Модели для валидации данных.
"""
from pydantic import BaseModel, Field


class UserIn(BaseModel):
    username: str = Field(max_length=32)
    email: str = Field(max_length=128)
    password: str = Field(max_length=50)


class UserOut(BaseModel):
    id: int = Field(..., ge=0)
    username: str = Field(max_length=32)
    email: str = Field(max_length=128)
    password: str = Field(max_length=50)
