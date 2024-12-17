from sqlalchemy.orm import Session
import models
import schemas

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.BookData(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BookData).offset(skip).limit(limit).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(models.BookData).filter(models.BookData.id == book_id).first()