# routers/invoices.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import Invoice
from ..schemas.schemas import InvoiceCreate, InvoiceResponse
from app.routers.auth import admin_required

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"]
)

@router.post("/", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, invoice_update: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in invoice_update.dict().items():
        setattr(db_invoice, key, value)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.delete("/{invoice_id}", response_model=dict)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(db_invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}