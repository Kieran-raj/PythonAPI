# TODO: Add some docstrings all functions
# TODO: Use an ORM instead of having multiple SQL databases - syntax then wont matter

import json
import calendar
from flask.wrappers import Response
from sqlalchemy import exc  # TODO: used for error handling
import pandas as pd
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from ..app import db
from api import chosen_config
from ..expenses.models.expenses import Expense
from ..expenses.helpers.functions import generate_response, convert_datetype_to_string
from ..config import TestConfig


bp = Blueprint("expenses", __name__, url_prefix="/expenses")
config = chosen_config[11:]

expenses_table = "expenses_prod.expenses"
if config == "DevConfig":
    expenses_table = "expenses_dev.expenses"
else:
    database_uri = TestConfig().SQLALCHEMY_DATABASE_URI
    expenses_table = "expenses"


# Define database engine and generate session

engine = db.create_engine(database_uri, {})
Session = sessionmaker(bind=engine)


@bp.route('/heartbeat', methods=['GET'])
def heartbeat():
    return generate_response(jsonify(message="API working"), 200)


@bp.route('/full_data', methods=['GET', 'POST'])
def full_data() -> Response:
    session = Session()
    sql_query = session.query(Expense).statement

    expenses_df = pd.read_sql(sql_query, engine)

    session.close()

    if expenses_df.empty:
        return generate_response('', 204)

    expenses_df = convert_datetype_to_string(expenses_df, 'date')
    total = expenses_df['amount'].sum()
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(
        data={"total": total, "transactions": data_final})
    return generate_response(return_json_object, 200)

    # TODO: Be able to pass specific years and get all data for that
    # Will probably need a new end point for that eg /full_data/year


@bp.route('/full_data/all_years', methods=['GET'])
def full_data_all_years():
    sql_query = f"""
    SELECT DISTINCT YEAR(date) as years FROM {expenses_table}
    """
    if config == "TestConfig":
        sql_query = f"""
        SELECT DISTINCT strftime('%Y', date) as years FROM {expenses_table}
        """
    expenses_df = pd.read_sql(sql_query, db.engine)

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = expenses_df["years"].values.tolist()
    return_json_object = jsonify(data={"years": data_final})
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
            return_json_object = jsonify(
                message="startDate, endDate and category are missing")
            return generate_response(return_json_object, 400)

        if category != '':
            sql_query = f"""
            SELECT * FROM {expenses_table}
            WHERE (DATE(date) BETWEEN '{start_date}' AND '{end_date}')
            AND category='{category}'
            ORDER BY date"""
        elif category == '':
            sql_query = f"""
            SELECT * FROM {expenses_table}
            WHERE (DATE(date) BETWEEN '{start_date}' AND '{end_date}')
            ORDER BY date
            """
        elif start_date == '' & end_date == '':
            sql_query = f"""
            SELECT * FROM {expenses_table}
            WHERE category='{category}'
            ORDER BY date
            """
        elif end_date == '':
            sql_query = f"""
            SELECT * FROM {expenses_table}
            WHERE (DATE(date) BETWEEN '{start_date}' AND MAX(date))
            ORDER BY date
            """
        elif start_date == '':
            sql_query = f"""
            SELECT * FROM {expenses_table}
            WHERE (DATE(date) BETWEEN MIN(date) AND '{end_date}')
            ORDER BY date
            """

        expenses_df = pd.read_sql(sql_query, db.engine)

        if expenses_df.empty:
            return generate_response('', 204)

        expenses_df['date'] = expenses_df['date'].dt.strftime('%Y-%m-%d')
        total = expenses_df['amount'].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(
            data={"total": total, "transactions": data_final})
        return generate_response(return_json_object, 200)


@bp.route('/get_daily_amounts', methods=['GET'])
def get_daily_amounts():
    sql_query = f"""
    SELECT date, SUM(amount) as amount FROM {expenses_table}
    GROUP BY date
    ORDER BY date
    """
    url_parameters = request.args
    if url_parameters:
        start_date = url_parameters.get('start_date')
        end_date = url_parameters.get('end_date')
        if len(url_parameters > 2):
            return generate_response(jsonify(message='Too many parameters. Options - start_date and end_date'), 400)
        if (start_date is None) and (end_date is None):
            return generate_response(jsonify(message=f'Invalid parameter - {", ".join([key for key in url_parameters.keys()])}'), 400)

    expenses_df = pd.read_sql(sql_query, db.engine)

    if expenses_df.empty:
        return generate_response('', 204)

    expenses_df = convert_datetype_to_string(expenses_df, 'date')
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"dailyAmounts": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_daily_amounts/moving_average', methods=['GET'])
def moving_average():
    # Pass in window=1 for example
    url_parameters = request.args
    window = 1
    if url_parameters:
        window = url_parameters.get('window')

        if len(url_parameters) > 1:
            return generate_response(jsonify(message='Too many parameters. Only supply window size'), 400)
        if window is None:
            return generate_response(jsonify(message=f'Invalid parameter - {", ".join([key for key in url_parameters.keys()])}'), 400)

    return_json_object = jsonify(data="Data (default window)")
    return generate_response(return_json_object, 200)


@bp.route('/get_weekly_amounts', methods=['GET'])
def get_weekly_amounts():
    sql_query = f"""
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
            {expenses_table}
        ) AS weekly_data
        LEFT JOIN (
        SELECT
            expense_id,
            YEAR(date) as 'year'
        FROM
            {expenses_table}
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
    if config == "TestConfig":
        sql_query = f"""
        SELECT
            week,
            year,
            SUM(amount) as amount
        FROM (
            SELECT
                expenses_id,
                strftime('%W', date) as week,
                amount
            FROM
                {expenses_table}
            ) AS weekly_data
            LEFT JOIN (
            SELECT
                expenses_id,
                strftime('%Y', date) as 'year'
            FROM
                {expenses_table}
            ) AS years
        ON (
            weekly_data.expenses_id = years.expenses_id
        )
        GROUP BY
            week,
            year
        ORDER BY
            week
        """
    expenses_df = pd.read_sql(sql_query, db.engine)

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"weeklyAmounts": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_monthly_amounts', methods=['GET'])
def get_monthly_amounts():
    sql_query = f"""
    SELECT 
        MONTH(date) as month, 
        YEAR(date) as year, 
        SUM(amount) as amount 
    FROM {expenses_table}
    GROUP BY 
        MONTH(date), 
        YEAR(date)
    ORDER BY 
        MONTH(date)
    """
    if config == "TestConfig":
        sql_query = f"""
        SELECT
            strftime('%m', date) as month,
            strftime('%Y', date) as year,
            SUM(amount) as amount
        FROM {expenses_table}
        GROUP BY
            month,
            year
        ORDER BY month
        """
    expenses_df = pd.read_sql(sql_query, db.engine)

    if expenses_df.empty:
        return generate_response('', 204)

    expenses_df['month'] = expenses_df['month'].apply(
        lambda x: calendar.month_name[int(x)])
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"monthlyAmounts": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_categorical_amounts', methods=['GET'])
def get_categorical_amount():
    sql_query = f"""
    SELECT category, SUM(amount) as amount FROM {expenses_table}
    GROUP BY category
    """
    expenses_df = pd.read_sql(sql_query, db.engine)

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_response_object = jsonify(data={"categoricalAmounts": data_final})
    return generate_response(return_response_object, 200)
