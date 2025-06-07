# backend/app/routers/exams.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import re

from app.database import get_db
from app.routers.line_auth import get_current_user, role_required
from app.schemas import schemas
from app.models import models
from app.core.security import admin_required

router = APIRouter(
    prefix="/exams",
    tags=["exams"],
)

# ----------------- Endpoint เดิม -----------------

# สร้างข้อสอบใหม่ (admin, teacher เท่านั้น)
@router.post("/", response_model=schemas.ExamRead)
def create_exam(
    exam: schemas.ExamCreate,
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin", "teacher"]))
):
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
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["student"]))  # ตรวจสอบ role ว่าเป็น student เท่านั้น
):
    exam = db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    student_id = user["user"].student_id
    if not student_id:
        raise HTTPException(status_code=403, detail="User is not a student")

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

# ----------------- Endpoint ใหม่: Import ข้อสอบ -----------------

def read_google_sheet(sheet_url: str) -> pd.DataFrame:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_service_account.json', scope)
    client = gspread.authorize(creds)
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid Google Sheet URL")
    sheet_key = match.group(1)
    sheet = client.open_by_key(sheet_key).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

@router.post("/import")
async def import_exam_file(
    file: UploadFile = File(None),
    sheet_url: str = Body(None),
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin", "teacher"]))
):
    # อ่านไฟล์หรือ Google Sheet
    if sheet_url:
        df = read_google_sheet(sheet_url)
    elif file:
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file.file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            raise HTTPException(status_code=400, detail="Only .xlsx, .csv, or Google Sheet URL are supported")
    else:
        raise HTTPException(status_code=400, detail="No file or sheet_url provided")
    
    # ตรวจสอบคอลัมน์หลัก
    required_cols = ['subject', 'grade', 'question_text', 'answer']
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {required_cols}")
    
    # หา columns ที่เป็น choice
    choice_cols = [col for col in df.columns if col.startswith('choice') and df[col].notnull().any()]
    if not choice_cols:
        raise HTTPException(status_code=400, detail="No choice columns found (choice1, choice2, ...)")
    
    for idx, row in df.iterrows():
        # หา/สร้าง exam
        exam = db.query(models.Exam).filter_by(subject=row['subject'], grade=row['grade']).first()
        if not exam:
            exam = models.Exam(subject=row['subject'], grade=row['grade'], name=f"{row['subject']} {row['grade']}")
            db.add(exam)
            db.commit()
            db.refresh(exam)
        # ตรวจสอบโจทย์ซ้ำ
        existing_q = db.query(models.Question).filter_by(exam_id=exam.exam_id, question_text=row['question_text']).first()
        if existing_q:
            continue  # ข้ามถ้ามีโจทย์นี้แล้วใน exam เดียวกัน
        # เพิ่ม question
        question = models.Question(
            exam_id=exam.exam_id,
            question_text=row['question_text'],
            question_type=row.get('question_type', 'normal'),
            media_url=row.get('image_url', None),
            table_html=row.get('table_html', None),
            explanation=row.get('explanation', None)
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        # เพิ่ม choices
        answer = str(row['answer']).strip()
        for i, col in enumerate(choice_cols, 1):
            choice_text = row.get(col, '')
            if choice_text:
                is_correct = (str(i) == answer or col == f'choice{answer}')
                choice = models.Choice(
                    question_id=question.question_id,
                    choice_text=choice_text,
                    is_correct=is_correct
                )
                db.add(choice)
        db.commit()
    return {"status": "success", "message": "Imported successfully"}