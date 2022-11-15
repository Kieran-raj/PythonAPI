"""Class representing the Expenses table."""

from sqlalchemy.types import String, DATETIME, Integer, FLOAT
from sqlalchemy.schema import Column
from api.app import db


class Expense(db.Model):
    """
    A class to represent the Expenses Table.

    ...

    Attributes
    ----------
    expenses_id : int
        Unique ID for each expense record.
    date : DateTime
        Date the record was created or updated.
    description : str
        Description of the expense.
    catergory : str
        The category of the expense.
    amount : float
        The amount of the expense.
    """

    __tablename__ = "expenses"
    expenses_id = Column(Integer, primary_key=True)
    date = Column(DATETIME)
    description = Column(String(225))
    category = Column(String(50))
    amount = Column(FLOAT)

    def __repr__(self) -> str:
        return f"<Expense {self.expenses_id}>"
