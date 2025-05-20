from fastapi import APIRouter

router = APIRouter(
    prefix="/enrollments",
    tags=["enrollments"]
)

# ตัวอย่าง endpoint (ลบออกได้ถ้ายังไม่ใช้)
@router.get("/")
def read_enrollments():
    return {"message": "List of enrollments"}