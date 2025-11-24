from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
except ImportError:  # Pydantic v1 fallback
    ConfigDict = None

from app.models.expense_model import ExpenseCategory, ExpenseStatus


class EnumModel(BaseModel):
    if ConfigDict:
        model_config = ConfigDict(use_enum_values=True, populate_by_name=True)
    else:
        class Config:
            use_enum_values = True
            allow_population_by_field_name = True


class ExpenseBase(EnumModel):
    user_id: int = Field(..., description="Identificador del usuario dueño del gasto")
    category: ExpenseCategory = Field(default=ExpenseCategory.OTHERS)
    description: Optional[str] = Field(None, max_length=255)
    amount: Decimal = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1)
    installments: Optional[int] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    is_recurring: bool = False


class ExpenseCreate(ExpenseBase):
    status: ExpenseStatus = ExpenseStatus.POSTED
    category_label: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Etiqueta en español proveniente del frontend (ej. 'Servicios básicos')",
    )


class ExpenseUpdate(EnumModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, max_length=255)
    amount: Optional[Decimal] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=1)
    installments: Optional[int] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    transaction_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    category_label: Optional[str] = Field(default=None, max_length=255)


class ExpenseResponse(ExpenseBase):
    id: int
    status: ExpenseStatus
    created_at: datetime
    updated_at: datetime

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    else:
        class Config(EnumModel.Config):
            orm_mode = True


class ExpenseSummary(BaseModel):
    category: ExpenseCategory
    total_amount: Decimal


class ExpenseItemPayload(EnumModel):
    description: str = Field(..., alias="name", max_length=255)
    amount: Optional[Decimal] = Field(default=None, alias="total", gt=0)
    unit_amount: Optional[Decimal] = Field(default=None, alias="monto", gt=0)
    quantity: int = Field(default=1, alias="cantidad", ge=1)
    installments: Optional[int] = Field(default=None, alias="cuotas", gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)


class ExpenseBatchCreate(EnumModel):
    user_id: int = Field(..., description="Identificador del propietario de los gastos")
    category: Optional[ExpenseCategory] = None
    category_label: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Etiqueta en español usada en el frontend",
    )
    status: ExpenseStatus = ExpenseStatus.POSTED
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    is_recurring: bool = False
    items: list[ExpenseItemPayload] = Field(..., min_length=1)


class ExpenseBatchResponse(EnumModel):
    created: list[ExpenseResponse]
    total_amount: Decimal = Field(..., description="Suma total de los gastos creados en la operación")
