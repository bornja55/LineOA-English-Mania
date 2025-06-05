from fastapi import APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.models import Course  # Import Course model if needed

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

# ตัวอย่าง endpoint (ลบออกได้ถ้ายังไม่ใช้)
@router.get("/")
def read_courses():
    return {"message": "List of courses"}