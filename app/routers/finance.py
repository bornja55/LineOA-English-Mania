from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import Income, Expense
from ..schemas.schemas import IncomeCreate, IncomeResponse, ExpenseCreate, ExpenseResponse

router = APIRouter(
    prefix="/finance",
    tags=["finance"]
)

# Income endpoints

@router.post("/income/", response_model=IncomeResponse)
def create_income(income: IncomeCreate, db: Session = Depends(get_db)):
    db_income = Income(**income.dict())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

@router.get("/income/{income_id}", response_model=IncomeResponse)
def get_income(income_id: int, db: Session = Depends(get_db)):
    db_income = db.query(Income).filter(Income.income_id == income_id).first()
    if not db_income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return db_income

@router.get("/income/", response_model=List[IncomeResponse])
def list_incomes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incomes = db.query(Income).offset(skip).limit(limit).all()
    return incomes

# Expense endpoints

@router.post("/expense/", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/expense/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense record not found")
    return db_expense

@router.get("/expense/", response_model=List[ExpenseResponse])
def list_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = db.query(Expense).offset(skip).limit(limit).all()
    return expenses