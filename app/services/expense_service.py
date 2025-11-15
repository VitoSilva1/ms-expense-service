from datetime import date, datetime
from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.expense_model import Expense, ExpenseCategory
from app.schemas.expense_schema import ExpenseCreate, ExpenseResponse, ExpenseSummary, ExpenseUpdate


def create_expense(db: Session, payload: ExpenseCreate) -> ExpenseResponse:
    expense = Expense(**payload.dict())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return ExpenseResponse.from_orm(expense)


def get_expense(db: Session, expense_id: int, user_id: Optional[int] = None) -> Expense:
    query = db.query(Expense).filter(Expense.id == expense_id)
    if user_id is not None:
        query = query.filter(Expense.user_id == user_id)
    expense = query.first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


def list_expenses(
    db: Session,
    *,
    user_id: int,
    category: Optional[ExpenseCategory] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Iterable[ExpenseResponse]:
    query = db.query(Expense).filter(Expense.user_id == user_id)
    if category:
        query = query.filter(Expense.category == category)
    if date_from:
        query = query.filter(Expense.transaction_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Expense.transaction_date <= datetime.combine(date_to, datetime.max.time()))
    expenses = query.order_by(Expense.transaction_date.desc()).all()
    return [ExpenseResponse.from_orm(expense) for expense in expenses]


def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate, user_id: Optional[int] = None) -> ExpenseResponse:
    expense = get_expense(db, expense_id, user_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return ExpenseResponse.from_orm(expense)


def delete_expense(db: Session, expense_id: int, user_id: Optional[int] = None) -> None:
    expense = get_expense(db, expense_id, user_id)
    db.delete(expense)
    db.commit()


def summarize_by_category(
    db: Session,
    *,
    user_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[ExpenseSummary]:
    filters = [Expense.user_id == user_id]
    if date_from:
        filters.append(Expense.transaction_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        filters.append(Expense.transaction_date <= datetime.combine(date_to, datetime.max.time()))

    result = (
        db.query(Expense.category.label("category"), func.sum(Expense.amount).label("total_amount"))
        .filter(and_(*filters))
        .group_by(Expense.category)
        .all()
    )

    return [
        ExpenseSummary(category=row.category, total_amount=row.total_amount or 0)
        for row in result
    ]
