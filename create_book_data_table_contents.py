from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベース接続文字列
dsn = "postgresql://postgres:527@host.docker.internal:5432/postgres"

# エンジンの作成
engine = create_engine(dsn)

# データベース作成
with engine.connect() as conn:
    conn.execute(text("commit"))
    conn.execute(text("CREATE DATABASE devhub"))

# 新しいデータベースに接続
dsn_devhub = "postgresql://postgres:527@host.docker.internal:5432/devhub"
engine_devhub = create_engine(dsn_devhub)

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
    created_at = Column(DateTime)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String)
    publication_year = Column(Integer)
    isbn = Column(String)
    price = Column(Float)
    description = Column(String)
    created_at = Column(DateTime)
    
# テーブルの作成
Base.metadata.create_all(engine_devhub)

# セッションの作成
Session = sessionmaker(bind=engine_devhub)
session = Session()

print("データベースとテーブルが正常に作成されました。")