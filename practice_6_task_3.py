"""
#### Задание №3
- Создать API для управления списком задач.
- Каждая задача должна содержать поля "название",
"описание" и "статус" (выполнена/не выполнена).
- API должен позволять выполнять CRUD операции с
задачами.
"""
import databases
from typing import List
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert, select, update, delete
from sqlalchemy import create_engine, CheckConstraint, Column, Integer, String, Boolean


DATABASE_URL = "sqlite:///database_practice_6_task_3.db"


database = databases.Database(DATABASE_URL)


Base = declarative_base()


class Task(Base):

    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), CheckConstraint('LENGTH(name) >= 2'))
    description = Column(String(32), CheckConstraint('LENGTH(description) >= 2'))
    status = Column(Boolean, default=False)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)


app = FastAPI()

class TaskIn(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    description: str = Field(min_length=2, max_length=32)
    status: bool = Field(...)


class TaskInForCreate(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    description: str = Field(min_length=2, max_length=32)


class TaskOut(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(min_length=2, max_length=32)
    description: str = Field(min_length=2, max_length=32)
    status: bool = Field(...)


@app.get("/create_fake_task/{count}")
async def create_fake_task(count: int = Path(..., ge=1)):

    for i in range(count):

        new_fake_task = \
            insert(Task).values(name=f'task_name_{i}',
                                description=f'task_description_{i}')
        await database.execute(new_fake_task)
    return {'message': f'{count} fake task create'}


@app.post("/tasks/", response_model=TaskOut)
async def create_one_task(task: TaskInForCreate):

    new_task = \
        insert(Task).values(name=task.name,
                            description=task.description)

    last_record_id = await database.execute(new_task)

    return {"id": last_record_id, **task.dict()}


@app.get("/tasks/", response_model=List[TaskOut])
async def read_all_tasks():

    sql_query = select(Task)
    answer = await database.fetch_all(sql_query)

    tasks = []

    for one_task in answer:
        tasks.append({
            "id": one_task[0],
            "name": one_task[1],
            "description": one_task[2],
            "status": True if one_task[3] else False
        })

    return JSONResponse(content=tasks, status_code=200)


@app.get("/tasks/{task_id}", response_model=TaskOut | None)
async def read_task(task_id: int = Path(..., ge=0)):

    query = select(Task).where(Task.id == task_id)
    answer = await database.fetch_one(query)

    if answer:

        return {
            "id": answer[0],
            "name": answer[1],
            "description": answer[2],
            "status": True if answer[3] else False
        }


@app.put("/tasks/{task_id}", response_model=TaskOut | None)
async def update_task(update_task: TaskIn, task_id: int = Path(..., ge=1)):

    query = update(Task).where(Task.id == task_id).values(**update_task.dict())

    if await database.execute(query):
        return {
            "id": task_id,
            "name": update_task.name,
            "description": update_task.description,
            "status": update_task.status
        }


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int = Path(..., ge=1)):

    query = delete(Task).where(Task.id == task_id)

    if await database.execute(query):
        return {'delete_task': task_id}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
