from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from app.routers.line_auth import get_current_user
from app.schemas import schemas
from app.models import models

router = APIRouter(
    prefix="/exams",
    tags=["exams"],
)

# สร้างข้อสอบใหม่
@router.post("/", response_model=schemas.ExamRead)
def create_exam(exam: schemas.ExamCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_exam = models.Exam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

# ดึงรายการข้อสอบทั้งหมด
@router.get("/", response_model=List[schemas.ExamRead])
def list_exams(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    exams = db.query(models.Exam).offset(skip).limit(limit).all()
    return exams

# ดึงรายละเอียดข้อสอบพร้อมคำถาม
@router.get("/{exam_id}", response_model=schemas.ExamDetail)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

# นักเรียนเริ่มสอบ (สร้าง student_exam record)
@router.post("/{exam_id}/start", response_model=schemas.StudentExamRead)
def start_exam(exam_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # ตรวจสอบข้อสอบ
    exam = db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    # ตรวจสอบว่าผู้ใช้เป็นนักเรียน
    student_id = user.student_id
    if not student_id:
        raise HTTPException(status_code=403, detail="User is not a student")
    # สร้าง student_exam
    student_exam = models.StudentExam(student_id=student_id, exam_id=exam_id, status="in_progress")
    db.add(student_exam)
    db.commit()
    db.refresh(student_exam)
    return student_exam

# ส่งคำตอบของนักเรียน
@router.post("/student_exams/{student_exam_id}/answers", response_model=schemas.StudentAnswerRead)
def submit_answer(student_exam_id: int, answer: schemas.StudentAnswerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # ตรวจสอบ student_exam
    student_exam = db.query(models.StudentExam).filter(models.StudentExam.student_exam_id == student_exam_id).first()
    if not student_exam:
        raise HTTPException(status_code=404, detail="Student exam not found")
    # ตรวจสอบสิทธิ์ผู้ใช้
    if student_exam.student_id != user.student_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    # บันทึกคำตอบ
    student_answer = models.StudentAnswer(student_exam_id=student_exam_id, **answer.dict())
    db.add(student_answer)
    db.commit()
    db.refresh(student_answer)
    return student_answer

# ดึงผลสอบของนักเรียน
@router.get("/student_exams/{student_exam_id}/results", response_model=schemas.StudentExamResult)
def get_exam_result(student_exam_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student_exam = db.query(models.StudentExam).filter(models.StudentExam.student_exam_id == student_exam_id).first()
    if not student_exam:
        raise HTTPException(status_code=404, detail="Student exam not found")
    if student_exam.student_id != user.student_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    # คำนวณหรือดึงผลสอบ (สมมติว่ามีฟิลด์ score)
    return student_exam

# TODO: เพิ่ม endpoint สำหรับดาวน์โหลดผลสอบ (PDF/Word) พร้อมลายน้ำ