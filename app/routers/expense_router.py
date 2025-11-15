from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.expense_model import ExpenseCategory
from app.schemas.expense_schema import ExpenseCreate, ExpenseResponse, ExpenseSummary, ExpenseUpdate
from app.services import expense_service

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    return expense_service.create_expense(db, expense_in)


@router.get("/", response_model=list[ExpenseResponse])
def list_expenses(
    user_id: int = Query(...),
    category: Optional[ExpenseCategory] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    return expense_service.list_expenses(
        db,
        user_id=user_id,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/summary/by-category", response_model=list[ExpenseSummary])
def summarize_by_category(
    user_id: int = Query(...),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    return expense_service.summarize_by_category(
        db,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, user_id: Optional[int] = Query(default=None), db: Session = Depends(get_db)):
    expense = expense_service.get_expense(db, expense_id, user_id)
    return ExpenseResponse.from_orm(expense)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    return expense_service.update_expense(db, expense_id, payload, user_id)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, user_id: Optional[int] = Query(default=None), db: Session = Depends(get_db)):
    expense_service.delete_expense(db, expense_id, user_id)
