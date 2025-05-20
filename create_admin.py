# backend/create_admin.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.admin import Admin
from passlib.context import CryptContext

# สร้าง password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = "postgresql://mania_user:Xiufkja5569%@localhost:5433/english_mania"
engine = create_engine(DATABASE_URL)

# สร้าง tables (ถ้ายังไม่มี)
Base.metadata.create_all(bind=engine)

# สร้าง SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_admin(username: str, password: str):
    try:
        # Hash password
        hashed_password = pwd_context.hash(password)

        # สร้าง admin user
        admin = Admin(
            username=username,
            password_hash=hashed_password,
            role="admin"
        )

        # เพิ่มลงฐานข้อมูล
        db.add(admin)
        db.commit()
        print(f"Admin user '{username}' created successfully!")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # แก้ไข username และ password ตามต้องการ
    create_admin("siraphob.a", "Xiufkja5569%")