# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/book_review_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# models.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

class ReactionType(str, enum.Enum):
    GOOD = "good"
    BAD = "bad"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    bio = Column(String)
    profile_image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_books = relationship("UserBook", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    reactions = relationship("ReviewReaction", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String)
    author = Column(String)
    isbn = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_books = relationship("UserBook", back_populates="book")
    reviews = relationship("Review", back_populates="book")

class UserBook(Base):
    __tablename__ = "user_books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"))
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="user_books")
    book = relationship("Book", back_populates="user_books")

class Follows(Base):
    __tablename__ = "follows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    reactions = relationship("ReviewReaction", back_populates="review")

class ReviewReaction(Base):
    __tablename__ = "review_reactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"))
    reaction_type = Column(SQLAlchemyEnum(ReactionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reactions")
    review = relationship("Review", back_populates="reactions")

class UserStats(Base):
    __tablename__ = "user_stats"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    books_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    received_goods_count = Column(Integer, default=0)
    received_bads_count = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.utcnow)

# schemas.py
from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

class User(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BookBase(BaseModel):
    name: str
    url: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    content: str

class ReviewCreate(ReviewBase):
    book_id: UUID4

class ReviewUpdate(BaseModel):
    content: str

class Review(ReviewBase):
    id: UUID4
    user_id: UUID4
    book_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReviewReactionBase(BaseModel):
    reaction_type: ReactionType

class ReviewReactionCreate(ReviewReactionBase):
    review_id: UUID4

class ReviewReaction(ReviewReactionBase):
    id: UUID4
    user_id: UUID4
    review_id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import engine, get_db
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Review API")

# User endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: uuid.UUID, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Book endpoints
@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Review endpoints
@app.post("/reviews/", response_model=schemas.Review)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    db_review = models.Review(**review.dict(), user_id=current_user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/reviews/", response_model=List[schemas.Review])
def read_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).offset(skip).limit(limit).all()
    return reviews

@app.put("/reviews/{review_id}", response_model=schemas.Review)
def update_review(
    review_id: uuid.UUID,
    review: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    db_review = db.query(models.Review).filter(
        models.Review.id == review_id,
        models.Review.user_id == current_user_id
    ).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    for key, value in review.dict().items():
        setattr(db_review, key, value)
    
    db.commit()
    db.refresh(db_review)
    return db_review

# Review Reaction endpoints
@app.post("/reviews/{review_id}/reactions", response_model=schemas.ReviewReaction)
def create_review_reaction(
    review_id: uuid.UUID,
    reaction: schemas.ReviewReactionCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    # Check if reaction already exists
    existing_reaction = db.query(models.ReviewReaction).filter(
        models.ReviewReaction.review_id == review_id,
        models.ReviewReaction.user_id == current_user_id
    ).first()
    
    if existing_reaction:
        raise HTTPException(status_code=400, detail="Reaction already exists")
    
    db_reaction = models.ReviewReaction(
        user_id=current_user_id,
        review_id=review_id,
        reaction_type=reaction.reaction_type
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction

@app.delete("/reviews/{review_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
def delete_review_reaction(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    db_reaction = db.query(models.ReviewReaction).filter(
        models.ReviewReaction.review_id == review_id,
        models.ReviewReaction.user_id == current_user_id
    ).first()
    
    if db_reaction is None:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    db.delete(db_reaction)
    db.commit()
    return

# Follow endpoints
@app.post("/users/{user_id}/follow", status_code=status.HTTP_201_CREATED)
def follow_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    existing_follow = db.query(models.Follows).filter(
        models.Follows.follower_id == current_user_id,
        models.Follows.following_id == user_id
    ).first()
    
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following")
    
    db_follow = models.Follows(
        follower_id=current_user_id,
        following_id=user_id
    )
    db.add(db_follow)
    db.commit()
    return {"status": "success"}

@app.delete("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None  # In reality, this would come from auth
):
    db_follow = db.query(models.Follows).filter(
        models.Follows.follower_id == current_user_id,
        models.Follows.following_id == user_id
    ).first()
    
    if db_follow is None:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    
    db.delete(db_follow)
    db.commit()
    return

@app.get("/users/{user_id}/followers", response_model=List[schemas.User])
def get_followers(user_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    followers = db.query(models.User).join(
        models.Follows, models.Follows.follower_id == models.User.id
    ).filter(
        models.Follows.following_id == user_id
    ).offset(skip).limit(limit).all()
    return followers

@app.get("/users/{user_id}/following", response_model=List[schemas.User])
def get_following(user_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    following = db.query(models.User).join(
        models.Follows, models.Follows.following_id == models.User.id
    ).filter(
        models.Follows.follower_id == user_id
    ).offset(skip).limit(limit).all()
    return following

# UserBook endpoints
@app.post("/users/books/", response_model=schemas.Book)
def add_user_book(
    book_id: uuid.UUID,
    is_favorite: bool = False,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None
):
    existing_user_book = db.query(models.UserBook).filter(
        models.UserBook.user_id == current_user_id,
        models.UserBook.book_id == book_id
    ).first()
    
    if existing_user_book:
        raise HTTPException(status_code=400, detail="Book already added")
    
    db_user_book = models.UserBook(
        user_id=current_user_id,
        book_id=book_id,
        is_favorite=is_favorite
    )
    db.add(db_user_book)
    db.commit()
    
    return db.query(models.Book).filter(models.Book.id == book_id).first()

@app.put("/users/books/{book_id}/favorite")
def toggle_favorite_book(
    book_id: uuid.UUID,
    is_favorite: bool,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = None
):
    db_user_book = db.query(models.UserBook).filter(
        models.UserBook.user_id == current_user_id,
        models.UserBook.book_id == book_id
    ).first()
    
    if not db_user_book:
        raise HTTPException(status_code=404, detail="Book not found in user's library")
    
    db_user_book.is_favorite = is_favorite
    db.commit()
    return {"status": "success"}

@app.get("/users/{user_id}/books", response_model=List[schemas.Book])
def get_user_books(
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    favorites_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(models.Book).join(
        models.UserBook
    ).filter(models.UserBook.user_id == user_id)
    
    if favorites_only:
        query = query.filter(models.UserBook.is_favorite == True)
    
    return query.offset(skip).limit(limit).all()

# User Stats endpoints
@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: uuid.UUID, db: Session = Depends(get_db)):
    stats = db.query(models.UserStats).filter(
        models.UserStats.user_id == user_id
    ).first()
    
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return {
        "books_count": stats.books_count,
        "reviews_count": stats.reviews_count,
        "following_count": stats.following_count,
        "followers_count": stats.followers_count,
        "received_goods_count": stats.received_goods_count,
        "received_bads_count": stats.received_bads_count,
        "calculated_at": stats.calculated_at
    }

# Stats update background task
from fastapi.background import BackgroundTasks
from datetime import datetime, timedelta

async def update_user_stats(user_id: uuid.UUID, db: Session):
    stats = db.query(models.UserStats).filter(
        models.UserStats.user_id == user_id
    ).first()
    
    if not stats:
        stats = models.UserStats(user_id=user_id)
        db.add(stats)
    
    # Update counts
    stats.books_count = db.query(models.UserBook).filter(
        models.UserBook.user_id == user_id
    ).count()
    
    stats.reviews_count = db.query(models.Review).filter(
        models.Review.user_id == user_id
    ).count()
    
    stats.following_count = db.query(models.Follows).filter(
        models.Follows.follower_id == user_id
    ).count()
    
    stats.followers_count = db.query(models.Follows).filter(
        models.Follows.following_id == user_id
    ).count()
    
    # Get reaction counts
    good_reactions = db.query(models.ReviewReaction).join(
        models.Review
    ).filter(
        models.Review.user_id == user_id,
        models.ReviewReaction.reaction_type == ReactionType.GOOD
    ).count()
    
    bad_reactions = db.query(models.ReviewReaction).join(
        models.Review
    ).filter(
        models.Review.user_id == user_id,
        models.ReviewReaction.reaction_type == ReactionType.BAD
    ).count()
    
    stats.received_goods_count = good_reactions
    stats.received_bads_count = bad_reactions
    stats.calculated_at = datetime.utcnow()
    
    db.commit()

# Search endpoints
@app.get("/search/books", response_model=List[schemas.Book])
def search_books(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Book).filter(
        models.Book.name.ilike(f"%{query}%") |
        models.Book.author.ilike(f"%{query}%") |
        models.Book.isbn.ilike(f"%{query}%")
    ).offset(skip).limit(limit).all()

@app.get("/search/reviews", response_model=List[schemas.Review])
def search_reviews(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Review).filter(
        models.Review.content.ilike(f"%{query}%")
    ).offset(skip).limit(limit).all()

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config and environment variables
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)