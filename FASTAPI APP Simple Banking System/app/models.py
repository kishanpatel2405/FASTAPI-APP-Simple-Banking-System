from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


class AccountType(PyEnum):
    CHECKING = "checking"
    SAVINGS = "savings"


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    fee = Column(Float, default=0.0)
    interest_rate = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    account_id = Column(Integer, ForeignKey('accounts.id'))

    account = relationship("Account", back_populates="transactions")

