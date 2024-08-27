from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import get_db
from .models import Account, Transaction, AccountType
app = FastAPI()



class AccountCreate(BaseModel):
    owner: str
    balance: float
    account_type: AccountType
    interest_rate: float

@app.post("/accounts/")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    fee = 0.0
    if account.account_type == AccountType.SAVINGS:
        fee = 5.0
    elif account.account_type == AccountType.CHECKING:
        fee = 10.0

    db_account = Account(
        owner=account.owner,
        balance=account.balance,
        account_type=account.account_type,
        fee=fee,
        interest_rate=account.interest_rate
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@app.get("/transactions/{account_id}")
def get_transaction_history(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.account_id == account_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return transactions


class UpdateAccount(BaseModel):
    balance: float
    account_type: AccountType


@app.patch("/accounts/{account_id}/update/")
def update_account(account_id: int, update: UpdateAccount, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update account balance and type
    account.balance = update.balance
    account.account_type = update.account_type

    # Update fee based on account type
    if account.account_type == AccountType.SAVINGS:
        account.fee = 5.0
    elif account.account_type == AccountType.CHECKING:
        account.fee = 10.0

    db.commit()
    db.refresh(account)
    return account


@app.get("/accounts/{account_id}/statement")
def get_statement(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "owner": account.owner,
        "balance": account.balance
    }


@app.get("/total_balance/")
def get_total_balance(db: Session = Depends(get_db)):
    total_balance = db.query(Account).with_entities(func.sum(Account.balance)).scalar()
    return {"total_balance": total_balance}


@app.post("/withdraw/")
def withdraw_from_account(atm_number: int, amount: float, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == atm_number).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    account.balance -= amount
    db.commit()

    return {"message": "Withdrawal successful", "new_balance": account.balance}


@app.post("/accounts/{account_id}/deposit/")
def deposit(account_id: int, amount: float, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.balance += amount
    db.commit()
    db.refresh(account)
    return {"message": "Deposit successful", "new_balance": account.balance}


@app.post("/transfer/")
def transfer(from_account_id: int, to_account_id: int, amount: float, db: Session = Depends(get_db)):
    from_account = db.query(Account).filter(Account.id == from_account_id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")

    if from_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    from_account.balance -= amount
    to_account.balance += amount

    db.commit()

    return {"message": "Transfer successful", "from_balance": from_account.balance, "to_balance": to_account.balance}



@app.get("/transactions/{account_id}")
def get_transaction_history(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.account_id == account_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return transactions


@app.patch("/accounts/{account_id}/apply_interest/")
def apply_interest(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    interest = account.balance * (account.interest_rate / 100)
    account.balance += interest
    db.commit()
    db.refresh(account)

    return {"message": "Interest applied successfully", "new_balance": account.balance}


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"detail": "Account deleted"}


@app.get("/transactions/{account_id}/from/{start_date}/to/{end_date}")
def get_transaction_history(account_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        # Parse the date strings to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS.")

    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.timestamp.between(start_date, end_date)
    ).all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this period.")

    return transactions