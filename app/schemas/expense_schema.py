from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, constr

from app.models.expense_model import ExpenseCategory, ExpenseStatus


class ExpenseBase(BaseModel):
    user_id: int = Field(..., description="Identificador del usuario dueño del gasto")
    category: ExpenseCategory = Field(default=ExpenseCategory.OTHER)
    description: Optional[str] = Field(None, max_length=255)
    amount: Decimal = Field(..., gt=0)
    installments: Optional[int] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    is_recurring: bool = False


class ExpenseCreate(ExpenseBase):
    status: ExpenseStatus = ExpenseStatus.POSTED


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, max_length=255)
    
    amount: Optional[Decimal] = Field(default=None, gt=0)
    installments: Optional[int] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    transaction_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None


class ExpenseResponse(ExpenseBase):
    id: int
    status: ExpenseStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ExpenseSummary(BaseModel):
    category: ExpenseCategory
    total_amount: Decimal
