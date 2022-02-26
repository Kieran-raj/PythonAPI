from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, DATETIME, Integer, FLOAT
from sqlalchemy.schema import Column
from api.app import db

class Expenses(db.Model):
    __tablename__ = "expenses"
    expense_id = Column(Integer, primary_key = True)
    date = Column(DATETIME)
    description = Column(String(225))
    category = Column(String(50))
    amount = Column(FLOAT)

    def __repr__(self) -> str:
        return f'<Expense {self.expense_id}>'