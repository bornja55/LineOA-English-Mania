from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import Enrollment, Invoice, Course
from ..schemas.schemas import EnrollmentCreate, EnrollmentResponse, InvoiceCreate
from datetime import datetime, timedelta, date

router = APIRouter(
    prefix="/enrollments",
    tags=["enrollments"]
)

from datetime import date

@router.post("/", response_model=EnrollmentResponse)
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    # สร้าง enrollment โดยกำหนด enroll_date เป็นวันนี้
    db_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        enroll_date=date.today(),  # ใช้ enroll_date แทน enrolled_at
        status="active"
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)

    # ดึงราคาคอร์สจริงจากตาราง course
    course = db.query(Course).filter(Course.course_id == enrollment.course_id).first()
    total_amount = course.price if course else 0

    # สร้าง invoice อัตโนมัติ
    invoice_data = InvoiceCreate(
        student_id=enrollment.student_id,
        enrollment_id=db_enrollment.enrollment_id,
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        total_amount=total_amount,
        description="Invoice for enrollment",
        status="pending"
    )
    db_invoice = Invoice(**invoice_data.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    return db_enrollment

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

@router.get("/", response_model=List[EnrollmentResponse])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).offset(skip).limit(limit).all()
    return enrollments

@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(enrollment_id: int, enrollment_update: EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    for key, value in enrollment_update.dict().items():
        setattr(db_enrollment, key, value)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@router.delete("/{enrollment_id}", response_model=dict)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(db_enrollment)
    db.commit()
    return {"message": "Enrollment deleted successfully"}