"""
#### Задание #1
- Разработать API для управления списком пользователей с
использованием базы данных SQLite. Для этого создайте
модель User со следующими полями:
○ id: int (идентификатор пользователя, генерируется
автоматически)
○ username: str (имя пользователя)
○ email: str (электронная почта пользователя)
○ password: str (пароль пользователя)
- API должно поддерживать следующие операции:
○ Получение списка всех пользователей: GET /users/
○ Получение информации о конкретном пользователе: GET /users/{user_id}/
○ Создание нового пользователя: POST /users/
○ Обновление информации о пользователе: PUT /users/{user_id}/
○ Удаление пользователя: DELETE /users/{user_id}/
- Для валидации данных используйте параметры Field модели User.
- Для работы с базой данных используйте SQLAlchemy и модуль databases.
"""
import databases
from typing import List
from fastapi import FastAPI, Path
from sqlalchemy import create_engine
#from contextlib import asynccontextmanager
from practice_6_task_1_models_db import Base, User
from sqlalchemy.sql import insert, select, update, delete
from practice_6_task_1_models_validation import UserOut, UserIn

DATABASE_URL = "sqlite:///database_practice_6_task_1.db"

database = databases.Database(DATABASE_URL)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/create_fake_users/{count}")
async def create_fake_users(count: int = Path(..., ge=1)):

    for i in range(count):

        new_fake_user = \
            insert(User).values(password=f'password_{i}',
                                username=f'user_{i}',
                                email=f'mail_user_{i}@mail.ru')
        await database.execute(new_fake_user)
    return {'message': f'{count} fake users create'}


@app.get("/users/", response_model=List[UserOut])
async def read_all_users():

    sql_query = select(User)
    answer = await database.fetch_all(sql_query)
    return answer


@app.get("/users/{user_id}", response_model=UserOut | None)
async def read_user(user_id: int = Path(..., ge=0)):

    query = \
        select(User).where(User.id == user_id)

    answer = \
        await database.fetch_one(query)

    if answer:
        return answer


@app.post("/users/", response_model=UserOut)
async def create_one_user(user: UserIn):

    new_user = insert(User).values(password=user.password,
                                   username=user.username,
                                   email=user.email)
    last_record_id = await database.execute(new_user)
    return {"id": last_record_id, **user.dict()}


@app.put("/users/{user_id}", response_model=UserOut | None)
async def update_user(new_user: UserIn, user_id: int = Path(..., ge=1)):

    query = \
        update(User).where(User.id == user_id).values(**new_user.dict())

    if await database.execute(query):
        return {"id": user_id, **new_user.dict()}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int = Path(..., ge=1)):

    query = delete(User).where(User.id == user_id)

    if await database.execute(query):
        return {'deleted user': user_id}


#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    await database.connect()
#
#    yield
#
#    await database.disconnect()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
