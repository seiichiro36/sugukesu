from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

# データベース接続
dsn = "postgresql://postgres:527@localhost:5432/devhub"
engine = create_engine(dsn)

# ベースクラスの作成
Base = declarative_base()

# Bookモデルの定義
class BookData(Base):
    __tablename__ = 'book_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String)
    publication_year = Column(Integer)
    isbn = Column(String)
    price = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# モックデータの作成
mock_books = [
    BookData(
        title="Python入門",
        author="山田太郎",
        publication_year=2022,
        isbn="978-1234567890",
        price=2800.50,
        description="プログラミング初心者向けのPython学習書"
    ),
    BookData(
        title="データベース設計の基本",
        author="佐藤花子",
        publication_year=2021,
        isbn="978-0987654321",
        price=3200.00,
        description="データベース設計の原則と実践"
    ),
    BookData(
        title="機械学習超入門",
        author="鈴木次郎",
        publication_year=2023,
        isbn="978-5555555555",
        price=3500.75,
        description="機械学習の基本概念から実践まで"
    )
]

# データベースにモックデータを追加
try:
    session.add_all(mock_books)
    session.commit()
    print("モックデータの挿入に成功しました。")
except Exception as e:
    session.rollback()
    print(f"エラーが発生しました：{e}")
finally:
    session.close()