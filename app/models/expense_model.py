from datetime import datetime
from enum import Enum
import unicodedata

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String
from app.core.database import Base


class ExpenseCategory(str, Enum):
    SERVICE_BASIC = "service_basic"
    SUPERMARKET = "supermarket"
    CREDIT_CARD = "credit_card"
    BANK_DEBTS = "bank_debts"
    OTHERS = "others"


class ExpenseStatus(str, Enum):
    PLANNED = "planned"
    POSTED = "posted"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(
        SqlEnum(
            ExpenseCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ExpenseCategory.OTHERS,
    )
    description = Column(String(255))
    amount = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    installments = Column(Integer, nullable=True)
    payment_method = Column(String(50))
    status = Column(
        SqlEnum(
            ExpenseStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ExpenseStatus.POSTED,
    )
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Expense id={self.id} user_id={self.user_id} amount={self.amount}>"


_CATEGORY_LABELS = {
    "servicios basicos": ExpenseCategory.SERVICE_BASIC,
    "servicios basicos/otros": ExpenseCategory.SERVICE_BASIC,
    "supermercado": ExpenseCategory.SUPERMARKET,
    "tarjetas de credito": ExpenseCategory.CREDIT_CARD,
    "tarjetas credito": ExpenseCategory.CREDIT_CARD,
    "deudas bancarias": ExpenseCategory.BANK_DEBTS,
    "otras deudas": ExpenseCategory.OTHERS,
    "otros": ExpenseCategory.OTHERS,
}


def normalize_label(value: str) -> str:
    """Lowercase label stripping diacritics so front labels can be mapped easily."""
    normalized = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_marks.lower().strip()


def map_category_label(label: str) -> ExpenseCategory | None:
    if not label:
        return None
    return _CATEGORY_LABELS.get(normalize_label(label))
