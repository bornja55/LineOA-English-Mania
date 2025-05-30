# routers/enrollments.py
# FastAPI router for handling enrollment-related endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import Enrollment, Invoice
from ..schemas.schemas import EnrollmentCreate, EnrollmentResponse, InvoiceCreate, InvoiceResponse
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/enrollments",
    tags=["enrollments"]
)

@router.post("/", response_model=EnrollmentResponse)
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    # สร้าง enrollment
    db_enrollment = Enrollment(**enrollment.dict())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)

    # สร้าง invoice อัตโนมัติ
    invoice_data = InvoiceCreate(
        student_id=enrollment.student_id,
        enrollment_id=db_enrollment.id,
        invoice_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=7),
        total_amount=0,  # กำหนดตามราคาคอร์ส (ต้องดึงราคาคอร์สจริง)
        description="Invoice for enrollment",
        status="pending"
    )
    # ดึงราคาคอร์สจริง
    course = db.query(Enrollment).filter(Enrollment.id == db_enrollment.id).first()
    if course:
        # สมมติมี price ใน course
        course_obj = db.query(Invoice).filter(Invoice.enrollment_id == db_enrollment.id).first()
        if course_obj:
            invoice_data.total_amount = course_obj.total_amount

    db_invoice = Invoice(**invoice_data.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    return db_enrollment

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

@router.get("/", response_model=List[EnrollmentResponse])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).offset(skip).limit(limit).all()
    return enrollments

@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(enrollment_id: int, enrollment_update: EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    for key, value in enrollment_update.dict().items():
        setattr(db_enrollment, key, value)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@router.delete("/{enrollment_id}", response_model=dict)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(db_enrollment)
    db.commit()
    return {"message": "Enrollment deleted successfully"}