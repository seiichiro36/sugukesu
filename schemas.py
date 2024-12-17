from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookCreate(BaseModel):
    title: str
    author: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class BookResponse(BookCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True