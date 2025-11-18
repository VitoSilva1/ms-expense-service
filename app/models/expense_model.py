from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String
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


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(SqlEnum(ExpenseCategory), nullable=False, default=ExpenseCategory.OTHER)
    description = Column(String(255))
    amount = Column(Numeric(12, 2), nullable=False)
    installments = Column(Integer, nullable=True)
    payment_method = Column(String(50))
    status = Column(SqlEnum(ExpenseStatus), nullable=False, default=ExpenseStatus.POSTED)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Expense id={self.id} user_id={self.user_id} amount={self.amount}>"
