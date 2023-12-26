"""
Модели для базы данных .
"""
from sqlalchemy import Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    email = Column(String(128))
    password = Column(String(50))
