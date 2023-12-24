import databases
import sqlalchemy
from typing import List
from fastapi import FastAPI
from sqlalchemy.sql import insert, select, update, delete
from pydantic import BaseModel, Field
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String


DATABASE_URL = "sqlite:///mydatabase.db"


database = databases.Database(DATABASE_URL)


#metadata = sqlalchemy.MetaData()


#users = sqlalchemy.Table(
#    "users",
#    metadata,
#    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
#    sqlalchemy.Column("name", sqlalchemy.String(32)),
#    sqlalchemy.Column("email", sqlalchemy.String(128)),
#)


Base = declarative_base()


class Users(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    email = Column(String(128))


#engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


#metadata.create_all(engine)
Base.metadata.create_all(bind=engine)


app = FastAPI()


class UserIn(BaseModel):
    name: str = Field(max_length=32)
    email: str = Field(max_length=128)


class User(BaseModel):
    id: int
    name: str = Field(max_length=32)
    email: str = Field(max_length=128)


@app.get("/fake_users/{count}")
async def create_note(count: int):

    for i in range(count):

        new_user = insert(Users).values(name=f'user{i}', email=f'mail{i}@mail.ru')
        print('new_user')
        print(new_user)

        await database.execute(new_user)
    return {'message': f'{count} fake users create'}


@app.post("/users/", response_model=User)
async def create_user(user: UserIn):

    new_user = insert(Users).values(name=f'user{i}', email=f'mail{i}@mail.ru')
    last_record_id = await database.execute(new_user)
    return {**user.dict(), "id": last_record_id}


@app.get("/users/", response_model=List[User])
async def read_users():

    query = select(Users)
    print('---')
    print(query)

    return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):

    query = select(Users).where(Users.id == user_id)
    print('---')
    print(query)

    return await database.fetch_one(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):

    query = update(Users).where(Users.id == user_id).values(**new_user.dict())
    print('---')
    print(query)

    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):

    query = delete(Users).where(Users.id == user_id)
    print('---')
    print(query)

    await database.execute(query)
    return {'message': 'User deleted'}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
