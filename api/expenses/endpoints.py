# TODO: Add some docstrings all functions

import json
import calendar
import pandas as pd
from flask import Blueprint, request, jsonify
from api import db
from ..expenses.helpers.functions import generate_response

bp = Blueprint("expenses", __name__, url_prefix="/expenses")

@bp.route('/full_data', methods=['GET', 'POST'])
def full_data():
    if request.method == 'GET':
        sql_history = """
        SELECT * FROM expenses_dev.expenses
        ORDER BY date;
        """
        expenses_df = pd.read_sql(sql_history, db.engine)
        expenses_df['date'] = expenses_df['date'].dt.strftime('%Y-%m-%d')
        total = expenses_df['amount'].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(data={"total": total,"transactions":data_final})
        return generate_response(return_json_object, 200)

# TODO: Be able to pass specific years and get all data for that

@bp.route('/full_data/all_years', methods=['GET'])
def full_data_all_years():
    if request.method == 'GET':
        sql_query = """
        SELECT DISTINCT YEAR(date) as years FROM expenses_dev.expenses
        """
        expenses_df = pd.read_sql(sql_query, db.engine)
        data_final = expenses_df["years"].values.tolist()
        return_json_object = jsonify(data={"years":data_final})
        return generate_response(return_json_object, 200)


@bp.route('/filtered_data', methods=['GET'])
def filter_data():
    # start, end and category
    # start and end work
    # TODO: Make sure that all combinations are working
    start_date = request.args.get('startDate', default='')
    end_date = request.args.get('endDate', default='')
    category = request.args.get('category', default='')
    if request.method == "GET":
        if not start_date and not end_date and not category:
            return_json_object = jsonify(message="startDate, endDate and category are missing")
            return generate_response(return_json_object, 400)

        if category != '':
            sql_query = f"""
            SELECT * FROM expenses_dev.expenses
            WHERE (DATE(date) BETWEEN '{start_date}' AND '{end_date}')
            AND category='{category}'
            ORDER BY date"""
        elif category == '':
            sql_query = f"""
            SELECT * FROM expenses_dev.expenses
            WHERE (DATE(date) BETWEEN '{start_date}' AND '{end_date}')
            ORDER BY date
            """
        elif start_date == '' & end_date == '':
            sql_query = f"""
            SELECT * FROM expenses_dev.expenses
            WHERE category='{category}'
            ORDER BY date
            """
        elif end_date == '':
            sql_query = f"""
            SELECT * FROM expenses_dev.expenses
            WHERE (DATE(date) BETWEEN '{start_date}' AND MAX(date))
            ORDER BY date
            """
        elif start_date == '':
            sql_query = f"""
            SELECT * FROM expenses_dev.expenses
            WHERE (DATE(date) BETWEEN MIN(date) AND '{end_date}')
            ORDER BY date
            """
                  
        expenses_df = pd.read_sql(sql_query, db.engine)

        if expenses_df.empty:
            return generate_response('', 204)

        expenses_df['date'] = expenses_df['date'].dt.strftime('%Y-%m-%d')
        total = expenses_df['amount'].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(data={"total": total,"transactions":data_final})
        return generate_response(return_json_object, 200)


@bp.route('/get_daily_amounts', methods=['GET'])
def get_daily_amounts():
    sql_query = """
    SELECT date, SUM(amount) as amount FROM expenses_dev.expenses
    GROUP BY date
    ORDER BY date
    """
    expenses_df = pd.read_sql(sql_query, db.engine)
    expenses_df['date'] = expenses_df['date'].dt.strftime('%Y-%m-%d')
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"dailyAmounts":data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_weekly_amounts', methods=['GET'])
def get_weekly_amounts():
    sql_query = """
    SELECT
        week,
        year,
        SUM(amount) as amount
    FROM (
        SELECT
            expense_id,
            WEEK(date) as week,
            amount
        FROM
            expenses
        ) AS weekly_data
        LEFT JOIN (
        SELECT
            expense_id,
            YEAR(date) as 'year'
        FROM
            expenses
        ) AS years
    ON (
        weekly_data.expense_id = years.expense_id
    )
    GROUP BY
        week,
        year
    ORDER BY 
        week;
    """
    expenses_df = pd.read_sql(sql_query, db.engine)
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"weeklyAmounts":data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_monthly_amounts', methods=['GET'])
def get_monthly_amounts():
    sql_query = """
    SELECT 
        MONTH(date) as month, 
        YEAR(date) as year, 
        SUM(amount) as amount 
    FROM expenses_dev.expenses
    GROUP BY 
        MONTH(date), 
        YEAR(date)
    ORDER BY 
        MONTH(date)
    """
    expenses_df = pd.read_sql(sql_query, db.engine)
    expenses_df['month'] = expenses_df['month'].apply(lambda x: calendar.month_name[x])
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"monthlyAmounts":data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_categorical_amounts', methods=['GET'])
def get_categorical_amount():
    sql_query = """
    SELECT category, SUM(amount) as amount FROM expenses_dev.expenses
    GROUP BY category
    """
    expenses_df = pd.read_sql(sql_query, db.engine)
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_response_object = jsonify(data={"categoricalAmounts":data_final})
    return generate_response(return_response_object, 200)
