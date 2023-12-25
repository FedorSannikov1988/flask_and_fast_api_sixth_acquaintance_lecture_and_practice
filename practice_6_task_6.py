"""
#### Задание №6
- Необходимо создать базу данных для интернет-магазина. База данных должна
состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
содержать информацию о доступных товарах, их описаниях и ценах. Таблица
пользователи должна содержать информацию о зарегистрированных
пользователях магазина. Таблица заказы должна содержать информацию о
заказах, сделанных пользователями.
○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
имя, фамилия, адрес электронной почты и пароль.
○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
название, описание и цена.
○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
заказа.
- Создайте модели pydantic для получения новых данных и
возврата существующих в БД для каждой из трёх таблиц
(итого шесть моделей).
- Реализуйте CRUD операции для каждой из таблиц через
создание маршрутов, REST API (итого 15 маршрутов).
○ Чтение всех
○ Чтение одного
○ Запись
○ Изменение
○ Удаление
"""
import databases
from typing import List
from datetime import date
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert, select, update, delete
from sqlalchemy import CheckConstraint, create_engine, ForeignKey, Boolean, Integer, Column, String, Date


DATABASE_URL = "sqlite:///database_practice_6_task_6.db"


database = databases.Database(DATABASE_URL)


Base = declarative_base()


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), CheckConstraint('LENGTH(name) >= 2'), nullable=False)
    surname = Column(String(50), CheckConstraint('LENGTH(surname) >= 2'))
    email = Column(String(128), nullable=False)
    password = Column(String(50), CheckConstraint('LENGTH(password) >= 6'), nullable=False)


class Products(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), CheckConstraint('LENGTH(name) >= 2'), nullable=False)
    description = Column(String(50), CheckConstraint('LENGTH(description) >= 2'))
    price = Column(Integer, nullable=False)


class Orders(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    order_date = Column(Date, default=date.today(), nullable=False)
    status_order = Column(Boolean, default=False, nullable=False)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)


app = FastAPI()



@app.get("/create_fake_user/{count_new_user}")
async def create_fake_user(count_new_user: int = Path(..., ge=1)):

    for i in range(count_new_task):

        new_fake_task = \
            insert(Task).values(title=f'task_name_{i}',
                                description=f'task_description_{i}')
        await database.execute(new_fake_task)
    return {'message': f'{count_new_task} fake task create'}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
