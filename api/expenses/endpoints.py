import json
import re
import pandas as pd
from datetime import date
from flask import Blueprint, current_app as app, request, render_template, url_for
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        data = pd.read_sql(
            "SELECT * FROM expenses;", db.engine)

        if not data.empty:
            data['date'] = data['date'].dt.strftime('%Y-%m-%d')
            total = data['amount'].sum()
            data_final = json.loads(data.to_json(orient="records"))
            data_final[0]['total'] = total
            return render_template('home_page.html', data=data_final), 200
        else:
            return render_template('home_page.html', data=json.loads(data.to_json(orient="records"))), 200

    elif request.method == 'POST':
        if request.form['submit_button'] == 'Submit':
            description = request.form.get('description')
            amount = request.form.get('amount')
            category = request.form.get('category').capitalize()
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
            total = data['amount'].sum()
            data_final = json.loads(data.to_json(orient="records"))
            data_final[0]['total'] = total
            return render_template('home_page.html', data=data_final)


@bp.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'GET':
        # sql = f"""
        # SELECT date, SUM(amount)
        # FROM expenses_dev.expenses
        # GROUP BY date
        # """
        data = [("01-01-2020", 1597),
                ("02-01-2020", 1456),
                ("03-01-2020", 1908),
                ("04-01-2020", 896),
                ("05-01-2020", 755),
                ("06-01-2020", 453),
                ("07-01-2020", 1100),
                ("08-01-2020", 1235),
                ("09-01-2020", 1478)
                ]
        labels = [row[0] for row in data]
        values = [row[1] for row in data]

        return render_template("analytics_page.html", labels=labels, values=values)
