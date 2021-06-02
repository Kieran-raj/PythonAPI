import json
import pandas as pd
from datetime import date
from flask import Blueprint, current_app as app, request, render_template
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET'])
@bp.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('welcome_page.html'), 200


@bp.route('/enter_data', methods=['GET', 'POST'])
def enter_expense():
    if request.method == 'GET':
        data = pd.read_sql(
            "SELECT * FROM expenses;", db.engine)

        if not data.empty:
            data['date'] = data['date'].dt.strftime('%Y-%m-%d')

        return render_template('enter_data.html', data=json.loads(data.to_json(orient="records"))), 200

    elif request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category')
        today = date.today().strftime("%Y-%m-%d")

        insert_sql = f"""
        INSERT INTO expenses_dev.expenses
        (date, description, category, amount)
        VALUES ('{today}', '{description}', '{category}', '{float(amount)}');
        """
        db.engine.execute(insert_sql)
        data = pd.read_sql(
            "SELECT * FROM expenses;", db.engine)

        data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        return render_template('enter_data.html', data=json.loads(data.to_json(orient="records")))
