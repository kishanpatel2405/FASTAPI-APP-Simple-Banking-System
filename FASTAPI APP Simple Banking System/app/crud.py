from sqlalchemy.orm import Session
from app.models import Account
from app.schemas import AccountCreate


def create_account(db: Session, account: AccountCreate):
    db_account = Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_account(db: Session, account_id: int):
    return db.query(Account).filter(Account.id == account_id).first()


def transfer_funds(db: Session, from_account_id: int, to_account_id: int, amount: float):
    from_account = db.query(Account).filter(Account.id == from_account_id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()

    if from_account and to_account and from_account.balance >= amount:
        from_account.balance -= amount
        to_account.balance += amount
        db.commit()
        db.refresh(from_account)
        db.refresh(to_account)
        return {"status": "success"}
    return {"status": "failure"}
