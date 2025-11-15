from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, Integer, Numeric, String, Text
from app.core.database import Base


class ExpenseCategory(str, Enum):
    HOUSING = "housing"
    TRANSPORT = "transport"
    FOOD = "food"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    PERSONAL = "personal"
    SUBSCRIPTION = "subscription"
    DEBT = "debt"
    SAVINGS = "savings"
    OTHER = "other"


class ExpenseStatus(str, Enum):
    PLANNED = "planned"
    POSTED = "posted"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    category = Column(SqlEnum(ExpenseCategory), nullable=False, default=ExpenseCategory.OTHER)
    description = Column(String(255))
    notes = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    payment_method = Column(String(50))
    status = Column(SqlEnum(ExpenseStatus), nullable=False, default=ExpenseStatus.POSTED)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Expense id={self.id} user_id={self.user_id} amount={self.amount}>"
