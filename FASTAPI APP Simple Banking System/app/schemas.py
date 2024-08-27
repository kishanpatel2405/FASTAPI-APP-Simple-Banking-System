from pydantic import BaseModel


class AccountCreate(BaseModel):
    owner: str
    balance: float


class Account(BaseModel):
    id: int
    owner: str
    balance: float

    class Config:
        orm_mode = True
