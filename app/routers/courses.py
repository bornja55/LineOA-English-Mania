from fastapi import APIRouter

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

# ตัวอย่าง endpoint (ลบออกได้ถ้ายังไม่ใช้)
@router.get("/")
def read_courses():
    return {"message": "List of courses"}