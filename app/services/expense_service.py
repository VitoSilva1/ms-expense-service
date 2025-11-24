from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.expense_model import Expense, ExpenseCategory, ExpenseStatus, map_category_label
from app.schemas.expense_schema import (
    ExpenseBatchCreate,
    ExpenseBatchResponse,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseUpdate,
)


def _model_dump(instance, **kwargs):
    dump_method = getattr(instance, "model_dump", None)
    if callable(dump_method):
        return dump_method(**kwargs)
    dict_method = getattr(instance, "dict", None)
    if callable(dict_method):
        return dict_method(**kwargs)
    if isinstance(instance, dict):
        return instance
    raise TypeError("Unsupported payload type for _model_dump")


def _ensure_enum(value, enum_cls):
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    if isinstance(value, str):
        try:
            return enum_cls(value)
        except ValueError:
            try:
                return enum_cls[value.upper()]
            except KeyError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Valor inválido para {enum_cls.__name__}.",
                ) from exc
    return value


def _resolve_category(category_value, category_label):
    category = _ensure_enum(category_value, ExpenseCategory)
    if category:
        return category

    if category_label:
        mapped = map_category_label(category_label)
        if mapped:
            return mapped
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se reconoce la categoría '{category_label}'.",
        )

    return ExpenseCategory.OTHERS


def _prepare_amount_and_quantity(data):
    quantity = data.get("quantity") or 1
    try:
        quantity = int(quantity)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cantidad inválida.") from exc
    if quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor a 0.")
    data["quantity"] = quantity

    raw_amount = data.get("amount")
    try:
        amount = raw_amount if raw_amount is None or isinstance(raw_amount, Decimal) else Decimal(str(raw_amount))
    except (InvalidOperation, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Monto inválido.") from exc

    unit_amount = data.pop("unit_amount", None)
    if unit_amount is not None and not isinstance(unit_amount, Decimal):
        try:
            unit_amount = Decimal(str(unit_amount))
        except (InvalidOperation, TypeError) as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Monto inválido.") from exc

    if amount is None and unit_amount is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe especificar el monto del gasto.")

    if amount is None and unit_amount is not None:
        amount = unit_amount * quantity

    data["amount"] = amount


def _prepare_common_fields(data, *, category_label: Optional[str] = None):
    _prepare_category_and_status(data, category_label=category_label)
    _prepare_amount_and_quantity(data)
    return data


def _prepare_category_and_status(data, *, category_label: Optional[str] = None):
    data["category"] = _resolve_category(
        data.get("category"),
        data.pop("category_label", None) or category_label,
    )
    if "status" in data:
        data["status"] = _ensure_enum(data.get("status"), ExpenseStatus)
    return data


def _expense_to_response(expense: Expense) -> ExpenseResponse:
    return ExpenseResponse.from_orm(expense)


def create_expense(db: Session, payload: ExpenseCreate) -> ExpenseResponse:
    data = _prepare_common_fields(_model_dump(payload))
    expense = Expense(**data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return _expense_to_response(expense)


def create_expenses_batch(db: Session, payload: ExpenseBatchCreate) -> ExpenseBatchResponse:
    payload_data = _model_dump(payload)
    items = payload_data.pop("items", [])
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un gasto en 'items'.",
        )
    base_data = _prepare_category_and_status(payload_data)
    created: list[Expense] = []
    total_amount = Decimal("0")

    for item in items:
        item_data = _model_dump(item)
        expense_data = {
            **base_data,
            "description": item_data.get("description"),
            "amount": item_data.get("amount"),
            "unit_amount": item_data.get("unit_amount"),
            "quantity": item_data.get("quantity"),
            "installments": item_data.get("installments"),
            "payment_method": item_data.get("payment_method"),
        }
        _prepare_amount_and_quantity(expense_data)
        expense = Expense(**expense_data)
        db.add(expense)
        created.append(expense)

    db.commit()
    for expense in created:
        db.refresh(expense)
        total_amount += Decimal(expense.amount)

    responses = [_expense_to_response(expense) for expense in created]
    return ExpenseBatchResponse(created=responses, total_amount=total_amount)


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
    return [_expense_to_response(expense) for expense in expenses]


def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate, user_id: Optional[int] = None) -> ExpenseResponse:
    expense = get_expense(db, expense_id, user_id)
    updates = _model_dump(payload, exclude_unset=True)
    category_label = updates.pop("category_label", None)
    category_value = updates.pop("category", None)
    if category_value is not None or category_label:
        setattr(expense, "category", _resolve_category(category_value, category_label))

    for field, value in updates.items():
        if field == "status":
            value = _ensure_enum(value, ExpenseStatus)
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return _expense_to_response(expense)


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
