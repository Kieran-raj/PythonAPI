from ...app import db


class Expense(db.Model):
    __tablename__ = 'expenses'
    expenses_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATETIME, nullable=False)
    description = db.Column(db.String(225), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
