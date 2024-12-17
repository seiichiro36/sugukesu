from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:527@host.docker.internal/postgres"

engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        conn.execute(text("commit"))
        conn.execute(text("CREATE DATABASE devhub"))

    print("データベースとテーブルが正常に作成されました。")

if __name__ == "__main__":
    main()