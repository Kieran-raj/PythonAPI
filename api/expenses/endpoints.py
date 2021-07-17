import json
import pandas as pd
from datetime import date, datetime, timedelta
from flask import Blueprint, current_app as app, request, render_template, url_for
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    today = datetime.today().date()
    last_week = today - timedelta(days=7)

    if request.method == 'GET':
        sql = f"""
        SELECT * FROM expenses_dev.expenses 
        WHERE date >= '{last_week}' AND date <= '{today}'
        ORDER by date;
        """
        data = pd.read_sql(
            sql, db.engine)

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

            sql = f"""
            SELECT * FROM expenses_dev.expenses 
            WHERE date >= '{last_week}' AND date <= '{today}'
            ORDER by date;
            """
            data = pd.read_sql(sql, db.engine)
            if not data.empty:
                data['date'] = data['date'].dt.strftime('%Y-%m-%d')
                total = data['amount'].sum()
                data_final = json.loads(data.to_json(orient="records"))
                data_final[0]['total'] = total
                return render_template('home_page.html', data=data_final)
            else:
                return render_template('home_page.html', data=json.loads(data.to_json(orient="records"))), 200


@bp.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'GET':
        sql_expenses = f"""
        SELECT date, SUM(amount) AS amount
        FROM expenses_dev.expenses
        GROUP BY date
        ORDER by date
        """
        expenses_df = pd.read_sql(sql_expenses, db.engine)

        line_labels = []
        line_values = []
        for row in expenses_df.values:
            line_labels.append(row[0].date().strftime("%Y-%m-%d"))
            line_values.append(row[1])

        sql_savings = """
        SELECT savings, monthly_income
        FROM expenses_dev.users
        """

        savings_df = pd.read_sql(sql_savings, db.engine)

        pie_labels = []
        pie_values = []

        for col in savings_df:
            pie_values.append(float(savings_df[col].values))
            col = col.capitalize().replace('_', ' ')
            pie_labels.append(col)

        sql_monthly_spend = f"""
        SELECT MONTH(date) AS month, SUM(amount) AS monthly_sum FROM expenses_dev.expenses
        GROUP BY MONTH(date)
        """
        month_spend_pd = pd.read_sql(sql_monthly_spend, db.engine)

        pie_labels.append('Monthly Spending')
        pie_values.append(month_spend_pd['monthly_sum'][0])

        pie_percentages = [x / sum(pie_values) * 100 for x in pie_values]

        return render_template("analytics_page.html", line_labels=line_labels, line_values=line_values,
                               pie_labels=pie_labels, pie_percentages=pie_percentages)
