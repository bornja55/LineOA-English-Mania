from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import models
from .routers import students, courses, enrollments, auth, line_auth, line_webhook, invoice, finance


# สร้างตารางในฐานข้อมูล (ถ้ายังไม่มี)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="English Mania API",
    description="API for English Mania School Management System",
    version="1.0.0"
)

# กำหนดโดเมนที่อนุญาตให้เข้าถึง API (แก้เป็นโดเมน frontend ของคุณ)
origins = [
    "https://bornja55.github.io",  # ตัวอย่างโดเมน LIFF app
    "http://localhost",
    "http://localhost:3000",
    # เพิ่มโดเมนอื่น ๆ ที่ต้องการอนุญาต
]

# เพิ่ม CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # หรือใช้ ["*"] สำหรับทดสอบ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# เพิ่ม routers
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(auth.router)
app.include_router(line_auth.router)
app.include_router(line_webhook.router)
app.include_router(invoice.router)
app.include_router(finance.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to English Mania API"}