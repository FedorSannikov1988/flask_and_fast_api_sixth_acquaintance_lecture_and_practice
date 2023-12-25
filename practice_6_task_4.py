"""
#### Задание №4
- Напишите API для управления списком задач. Для этого
создайте модель Task со следующими полями:
○ id: int (первичный ключ)
○ title: str (название задачи)
○ description: str (описание задачи)
○ done: bool (статус выполнения задачи)
- API должно поддерживать следующие операции:
○ Получение списка всех задач: GET /tasks/
○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
○ Создание новой задачи: POST /tasks/
○ Обновление информации о задаче: PUT /tasks/{task_id}/
○ Удаление задачи: DELETE /tasks/{task_id}/
- Для валидации данных используйте параметры Field модели Task.
- Для работы с базой данных используйте SQLAlchemy и
модуль databases.
"""
import databases
from typing import List
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert, select, update, delete
from sqlalchemy import CheckConstraint, create_engine, Boolean, Integer, Column, String


DATABASE_URL = "sqlite:///database_practice_6_task_4.db"


database = databases.Database(DATABASE_URL)


Base = declarative_base()


class Task(Base):

    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), CheckConstraint('LENGTH(title) >= 2'))
    description = Column(String(500), CheckConstraint('LENGTH(description) >= 2'))
    done = Column(Boolean, default=False)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)


app = FastAPI()


class TaskIn(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=500)
    done: bool = Field(...)


class TaskInForCreate(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=500)


class TaskOut(BaseModel):
    id: int = Field(..., ge=1)
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=500)
    done: bool = Field(...)


@app.get("/create_fake_task/{count_new_task}")
async def create_fake_task(count_new_task: int = Path(..., ge=1)):

    for i in range(count_new_task):

        new_fake_task = \
            insert(Task).values(title=f'task_name_{i}',
                                description=f'task_description_{i}')
        await database.execute(new_fake_task)
    return {'message': f'{count_new_task} fake task create'}


@app.get("/tasks/", response_model=List[TaskOut])
async def read_all_tasks():

    sql_query = select(Task)

    answer = await database.fetch_all(sql_query)

    tasks: list = []

    for one_task in answer:
        tasks.append({
            "id": one_task[0],
            "title": one_task[1],
            "description": one_task[2],
            "done": True if one_task[3] else False
        })

    return JSONResponse(content=tasks, status_code=200)


@app.get("/tasks/{task_id}", response_model=TaskOut | None)
async def read_task(task_id: int = Path(..., ge=1)):

    query = select(Task).where(Task.id == task_id)
    answer = await database.fetch_one(query)

    if answer:

        return {
            "id": answer[0],
            "title": answer[1],
            "description": answer[2],
            "done": True if answer[3] else False
        }


@app.post("/tasks/", response_model=TaskOut)
async def create_one_task(task: TaskInForCreate):

    new_task = \
        insert(Task).values(title=task.title,
                            description=task.description)

    last_record_id = await database.execute(new_task)

    create_task = {"id": last_record_id, **task.dict(), "done": False}

    return JSONResponse(content=create_task, status_code=200)


@app.put("/tasks/{task_id}", response_model=TaskOut | None)
async def update_task(update_task: TaskIn, task_id: int = Path(..., ge=1)):

    query = update(Task).where(Task.id == task_id).values(**update_task.dict())

    if await database.execute(query):
        return {
            "id": task_id,
            "title": update_task.title,
            "description": update_task.description,
            "done": update_task.done
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
