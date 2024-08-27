from sqlalchemy import create_engine
from app.models import Base

SQLALCHEMY_DATABASE_URL = 'postgresql://bank_user:123@localhost/banking_system'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(bind=engine)
