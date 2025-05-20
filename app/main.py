from fastapi import FastAPI
from .database import engine
from .models import models
from .routers import students, courses, enrollments, auth

# สร้างตารางในฐานข้อมูล (ถ้ายังไม่มี)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="English Mania API",
    description="API for English Mania School Management System",
    version="1.0.0"
)

# เพิ่ม routers
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to English Mania API"}