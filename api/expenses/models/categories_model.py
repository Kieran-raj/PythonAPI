"Class representing the Categories table."

from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column
from api.app import db

class Categories(db.Model):
    """
    A class to present the Categories table

    ...
    """
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    category = Column(String(50)) 


    def __repr__(self) -> str:
        return f"<Category {self.id}>"