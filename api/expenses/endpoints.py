# TODO: Add some docstrings all functions

from datetime import datetime
import json
import calendar
from operator import and_
from flask.wrappers import Response
from sqlalchemy import engine, exc, func, distinct # TODO: used for error handling
import pandas as pd
from flask import Blueprint, request, jsonify
from api import db
from api.expenses.models.expenses_model import Expenses
from ..expenses.helpers.functions import generate_response, convert_datetype_to_string, convert_orm_object_to_dict


bp = Blueprint("expenses", __name__, url_prefix="/expenses")

@bp.route('/heartbeat', methods=['GET'])
def heartbeat():
    return generate_response(jsonify(message="API working"), 200)


@bp.route('/full_data', methods=['GET', 'POST'])
def full_data() -> Response:
    database_session = db.session()
    if request.method == 'GET':
        expenses = database_session.query(Expenses.expense_id, Expenses.date,\
            Expenses.description, Expenses.category, Expenses.amount)\
                .order_by(Expenses.date)

        database_session.close()
        columns = ["expense_id", "date", "description", "category", "amount"]
        expense_dict = convert_orm_object_to_dict(expenses, columns)
        expenses_df = pd.DataFrame.from_dict(expense_dict)

        if expenses_df.empty:
            return generate_response('', 204)

        expenses_df = convert_datetype_to_string(expenses_df, 'date')
        total = expenses_df['amount'].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(
            data={"total": total, "transactions": data_final})
        return generate_response(return_json_object, 200)

# Be able to pass specific years and get all data for that
# Will probably need a new end point for that eg /full_data/year


@bp.route('/full_data/all_years', methods=['GET'])
def full_data_all_years():
    database_session = db.session()
    expenses = database_session.query(distinct(func.extract("year", Expenses.date)))
    database_session.close()
    expenses_dict = {'years': [i[0] for i in expenses]}
    expenses_df = pd.DataFrame.from_dict((expenses_dict))

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = expenses_df["years"].values.tolist()
    return_json_object = jsonify(data={"years": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/filtered_data', methods=['GET'])
def filter_data():
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = request.args.get('startDate', default='1900-01-01')
    end_date = request.args.get('endDate', default=today)
    category = request.args.get('category', default='')
    database_session = db.session()
    if request.method == "GET":
        if not start_date and not end_date and not category:
            return_json_object = jsonify(
                message="startDate, endDate and category are missing")
            database_session.close()
            return generate_response(return_json_object, 400)

        expenses = database_session.query(Expenses.expense_id, Expenses.date,\
            Expenses.description, Expenses.category, Expenses.amount)\
                .filter(and_(Expenses.date >= start_date, Expenses.date <= end_date))\
                    .order_by(Expenses.date)
        
        if category != '':
            expenses = database_session.query(Expenses.expense_id, Expenses.date,\
            Expenses.description, Expenses.category, Expenses.amount)\
                .filter(and_(Expenses.date >= start_date, Expenses.date <= end_date))\
                    .filter(Expenses.category == category).\
                        order_by(Expenses.date)
        
        columns = ["expense_id", "date", "description", "category", "amount"]
        expense_dict = convert_orm_object_to_dict(expenses, columns)
        expenses_df = pd.DataFrame.from_dict(expense_dict)
        
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
    database_session = db.session()
    expenses = database_session.query(Expenses.date, func.sum(Expenses.amount).label('amount')).group_by(Expenses.date).order_by(Expenses.date)
    database_session.close()
    expense_dict = convert_orm_object_to_dict(expenses, ["date", "amount"])
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response('', 204)

    expenses_df = convert_datetype_to_string(expenses_df, 'date')
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"transactions": data_final})
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
    database_session = db.session()
    expenses = database_session.query(func.extract("week", Expenses.date).label("week"),\
       func.extract("year", Expenses.date).label("year"),\
           func.sum(Expenses.amount).label("amount"))\
               .group_by(func.extract("week", Expenses.date),\
                    func.extract("year", Expenses.date))\
                        .order_by(func.extract("week", Expenses.date))
    database_session.close()
    chosen_columns = ["week", "year", "amount"]

    expense_dict = convert_orm_object_to_dict(expenses, chosen_columns)
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"weeklyAmounts": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_monthly_amounts', methods=['GET'])
def get_monthly_amounts():
    database_session = db.session()
    expenses = database_session.query(func.extract("month", Expenses.date).label("month"),\
        func.extract("year", Expenses.date).label("year"),\
            func.sum(Expenses.amount).label("amount"))\
                .group_by(func.extract("month", Expenses.date), func.extract("year", Expenses.date))\
                    .order_by(func.extract("month", Expenses.date))
    database_session.close()
    chosen_columns = ["month", "year", "amount"]
    expense_dict = convert_orm_object_to_dict(expenses, chosen_columns)
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response('', 204)

    expenses_df['month'] = expenses_df['month'].apply(
        lambda x: calendar.month_name[int(x)])
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"monthlyTransactions": data_final})
    return generate_response(return_json_object, 200)


@bp.route('/get_categorical_amounts', methods=['GET'])
def get_categorical_amount():
    database_session = db.session()
    expenses = database_session.query(Expenses.category, func.sum(Expenses.amount).label("amount"))\
        .group_by(Expenses.category)
    database_session.close()
    expense_dict = convert_orm_object_to_dict(expenses, ["category", "amount"])
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response('', 204)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_response_object = jsonify(data={"categoricalAmounts": data_final})
    return generate_response(return_response_object, 200)
