from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# โหลดตัวแปรจาก .env
load_dotenv()

# สร้าง database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# สร้าง engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# สร้าง SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()