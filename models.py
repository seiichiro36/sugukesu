# from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from database import Base

# from datetime import datetime


# class Book(Base):
#     __tablename__ = "book"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     title = Column(String, nullable=False)
#     author = Column(String)
#     isbn = Column(String)
#     image_url=Column(String)
#     book_url=Column(String)
#     created_at = Column(DateTime)

from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class BookData(Base):
    __tablename__ = 'book_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String)
    publication_year = Column(Integer)
    isbn = Column(String)
    price = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)