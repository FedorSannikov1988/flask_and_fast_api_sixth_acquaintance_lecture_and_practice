"""
#### Задание #2
- Создать веб-приложение на FastAPI, которое будет предоставлять API
для работы с базой данных пользователей. Пользователь должен иметь
следующие поля:
○ ID (автоматически генерируется при создании пользователя)
○ Имя (строка, не менее 2 символов)
○ Фамилия (строка, не менее 2 символов)
○ Дата рождения (строка в формате "YYYY-MM-DD")
○ Email (строка, валидный email)
○ Адрес (строка, не менее 5 символов)
- API должен поддерживать следующие операции:
○ Добавление пользователя в базу данных
○ Получение списка всех пользователей в базе данных
○ Получение пользователя по ID
○ Обновление пользователя по ID
○ Удаление пользователя по ID
- Приложение должно использовать базу данных SQLite3 для
хранения пользователей.
"""
import databases
from typing import List
from datetime import date
from fastapi import FastAPI, Path
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert, select, update, delete
from sqlalchemy import create_engine, Column, Integer, String, Date, CheckConstraint


DATABASE_URL = "sqlite:///database_practice_6_task_2.db"


database = databases.Database(DATABASE_URL)


Base = declarative_base()


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(32), CheckConstraint('LENGTH(user_name) >= 2'))
    user_surname = Column(String(32), CheckConstraint('LENGTH(user_surname) >= 2'))
    date_birth = Column(Date)
    email = Column(String(128))
    address = Column(String(50), CheckConstraint('LENGTH(address) >= 5'))


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)


app = FastAPI()


class UserIn(BaseModel):
    user_name: str = Field(min_length=2, max_length=32)
    user_surname: str = Field(min_length=2, max_length=32)
    date_birth: date = Field(...)
    email: EmailStr = Field(max_length=128)
    address: str = Field(min_length=5, max_length=50)


class UserOut(BaseModel):
    id: int = Field(..., gt=0)
    user_name: str = Field(min_length=2, max_length=32)
    user_surname: str = Field(min_length=2, max_length=32)
    date_birth: date = Field(...)
    email: EmailStr = Field(max_length=128)
    address: str = Field(min_length=5, max_length=50)


@app.get("/create_fake_users/{count}")
async def create_fake_users(count: int = Path(..., ge=1)):

    for i in range(count):

        new_fake_user = \
            insert(User).values(user_name=f'user_name_{i}',
                                user_surname=f'user_surname_{i}',
                                date_birth=date.today(),
                                email=f'user_name_{i}@mail.com',
                                address=f'user_address_{i}')
        await database.execute(new_fake_user)
    return {'message': f'{count} fake users create'}


@app.post("/users/", response_model=UserOut)
async def create_one_user(user: UserIn):

    new_user = \
        insert(User).values(user_name=user.user_name,
                            user_surname=user.user_surname,
                            date_birth=user.date_birth,
                            email=user.email,
                            address=user.address)

    last_record_id = await database.execute(new_user)

    return {"id": last_record_id, **user.dict()}


@app.get("/users/", response_model=List[UserOut])
async def read_all_users():

    sql_query = select(User)
    answer = await database.fetch_all(sql_query)
    return answer


@app.get("/users/{user_id}", response_model=UserOut | None)
async def read_user(user_id: int = Path(..., ge=0)):

    query = select(User).where(User.id == user_id)
    answer = await database.fetch_one(query)

    if answer:
        return answer


@app.put("/users/{user_id}", response_model=UserOut | None)
async def update_user(new_user: UserIn, user_id: int = Path(..., ge=1)):

    query = update(User).where(User.id == user_id).values(**new_user.dict())

    if await database.execute(query):
        return {"id": user_id, **new_user.dict()}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int = Path(..., ge=1)):

    query = delete(User).where(User.id == user_id)

    if await database.execute(query):
        return {'Deleted user': user_id}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
