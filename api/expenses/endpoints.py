import json
import re
import pandas as pd
from datetime import date, datetime
from flask import Blueprint, current_app as app, request, render_template, url_for
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        data = pd.read_sql(
            "SELECT * FROM expenses ORDER by date;", db.engine)

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
            input_date = request.form.get('date')
            if input_date:
                final_date = datetime.strptime(input_date, '%Y-%m-%d')
            else:
                final_date = date.today().strftime("%Y-%m-%d")

            insert_sql = f"""
            INSERT INTO expenses_dev.expenses
            (date, description, category, amount)
            VALUES ('{final_date}', '{description}', '{category}', '{float(amount)}');
            """
            db.engine.execute(insert_sql)
            data = pd.read_sql(
                "SELECT * FROM expenses ORDER BY date;", db.engine)
            data['date'] = data['date'].dt.strftime('%Y-%m-%d')
            total = data['amount'].sum()
            data_final = json.loads(data.to_json(orient="records"))
            data_final[0]['total'] = total
            return render_template('home_page.html', data=data_final)


@bp.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'GET':
        sql = f"""
        SELECT date, SUM(amount) AS amount
        FROM expenses_dev.expenses
        GROUP BY date
        """
        df = pd.read_sql(sql, db.engine)

        labels = []
        values = []
        for row in df.values:
            labels.append(row[0].date().strftime("%Y-%m-%d"))
            values.append(row[1])

        return render_template("analytics_page.html", labels=labels, values=values)
