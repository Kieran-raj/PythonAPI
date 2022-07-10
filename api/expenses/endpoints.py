"Module that contains the end points and entry points to expenses API."

from datetime import datetime
from http import HTTPStatus
import json
import calendar
from operator import and_
from flask.wrappers import Response
from sqlalchemy import func, distinct
import pandas as pd
from flask import Blueprint, request, jsonify
from api import db
from api.expenses.models.expenses_model import Expenses
from api.expenses.models.full_data import FullData
from ..expenses.helpers.functions import (
    generate_response,
    convert_datetype_to_string,
    convert_orm_object_to_dict,
)


bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route("/heartbeat", methods=["GET"])
def heartbeat():
    """
    Heartbeat endpont to test api is up and running.
    ---
    get:
        summary: Heartbeat endpoint.
        description: Used to test to make sure the API is running
        responses:
            200:
                description: JSON object returned with message.
    """
    return generate_response(jsonify(message="API working"), HTTPStatus.OK)


@bp.route("/full_data", methods=["GET"])
def full_data() -> Response:
    """
    Full data endpoint.
    ---
    get:
        summary: Get all data endpoint.
        description: Get all historical data from the database.
        responses:
            200:
                description: Returns JSON object containing the total and transactions.
                schema: FullData
            204: Returns empty object.
    """
    database_session = db.session()
    if request.method == "GET":
        expenses = database_session.query(
            Expenses.expense_id,
            Expenses.date,
            Expenses.description,
            Expenses.category,
            Expenses.amount,
        ).order_by(Expenses.date)

        database_session.close()
        columns = ["expense_id", "date", "description", "category", "amount"]
        expense_dict = convert_orm_object_to_dict(expenses, columns)
        expenses_df = pd.DataFrame.from_dict(expense_dict)

        if expenses_df.empty:
            return generate_response("", HTTPStatus.PARTIAL_CONTENT)

        expenses_df = convert_datetype_to_string(expenses_df, "date")
        total = expenses_df["amount"].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(data={"total": total, "transactions": data_final})
        return generate_response(return_json_object, HTTPStatus.OK)

    return 0


# Be able to pass specific years and get all data for that
# Will probably need a new end point for that eg /full_data/year


@bp.route("/full_data/all_years", methods=["GET"])
def full_data_all_years():
    """
    All years endpoint.
    ---
    get:
        summary: All distinct years endpoint
        description: Get all the distinct years.
        responses:
            200:
                description: Returns all distinct years
                schema: {"years": List[int]}
            204:
                description: Returns empty object.
    """
    database_session = db.session()
    expenses = database_session.query(distinct(func.extract("year", Expenses.date)))
    database_session.close()
    expenses_dict = {"years": [i[0] for i in expenses]}
    expenses_df = pd.DataFrame.from_dict((expenses_dict))

    if expenses_df.empty:
        return generate_response("", HTTPStatus.PARTIAL_CONTENT)

    data_final = expenses_df["years"].values.tolist()
    return_json_object = jsonify(data={"years": data_final})
    return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/filtered_data", methods=["GET"])
def filter_data():
    """
    ---
    get:
        summary:
        description:
        parameters:
            - name: startDate
              in: path
              description: Start date
              type: string
              required: false
            - name: endDate
              in: path
              description: End date
              type: string
              required: false

            - name: category
              in: path
              description: Category
              type: string
              required: false
        responses:
            200:
                description: Return object containing data based on filters.
                schema: FullData
            204:
                description: Returns empty object.
            400:
                description: Bad Request
    """

    today = datetime.today().strftime("%Y-%m-%d")
    start_date = request.args.get("startDate", default="1900-01-01")
    end_date = request.args.get("endDate", default=today)
    category = request.args.get("category", default="")
    database_session = db.session()
    if request.method == "GET":
        if not start_date and not end_date and not category:
            return_json_object = jsonify(
                message="startDate, endDate and category are missing"
            )
            database_session.close()
            return generate_response(return_json_object, HTTPStatus.BAD_REQUEST)

        expenses = (
            database_session.query(
                Expenses.expense_id,
                Expenses.date,
                Expenses.description,
                Expenses.category,
                Expenses.amount,
            )
            .filter(and_(Expenses.date >= start_date, Expenses.date <= end_date))
            .order_by(Expenses.date)
        )

        if category != "":
            expenses = (
                database_session.query(
                    Expenses.expense_id,
                    Expenses.date,
                    Expenses.description,
                    Expenses.category,
                    Expenses.amount,
                )
                .filter(and_(Expenses.date >= start_date, Expenses.date <= end_date))
                .filter(Expenses.category == category)
                .order_by(Expenses.date)
            )

        columns = ["expense_id", "date", "description", "category", "amount"]
        expense_dict = convert_orm_object_to_dict(expenses, columns)
        expenses_df = pd.DataFrame.from_dict(expense_dict)

        if expenses_df.empty:
            return generate_response("", HTTPStatus.PARTIAL_CONTENT)

        expenses_df["date"] = expenses_df["date"].dt.strftime("%Y-%m-%d")
        total = expenses_df["amount"].sum()
        data_final = json.loads(expenses_df.to_json(orient="records"))
        return_json_object = jsonify(data={"total": total, "transactions": data_final})
        return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/get_daily_amounts", methods=["GET"])
def get_daily_amounts():
    """
    Daily amounts endpoint.
    ---
    get:
        summary: Get daily amounts endpoint.
        description: Get all daily amounts.
        responses:
            200:
                description: Returns JSON object containing daily amounts.
                schema: {"transactions": any}
            204: Returns empty object.
    """
    database_session = db.session()
    expenses = (
        database_session.query(Expenses.date, func.sum(Expenses.amount).label("amount"))
        .group_by(Expenses.date)
        .order_by(Expenses.date)
    )
    database_session.close()
    expense_dict = convert_orm_object_to_dict(expenses, ["date", "amount"])
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response("", HTTPStatus.PARTIAL_CONTENT)

    expenses_df = convert_datetype_to_string(expenses_df, "date")
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"transactions": data_final})
    return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/get_daily_amounts/moving_average", methods=["GET"])
def moving_average():
    # Pass in window=1 for example
    url_parameters = request.args
    window = 1
    if url_parameters:
        window = url_parameters.get("window")

        if len(url_parameters) > 1:
            return generate_response(
                jsonify(message="Too many parameters. Only supply window size"),
                HTTPStatus.BAD_REQUEST,
            )
        if window is None:
            return generate_response(
                jsonify(
                    message=f'Invalid parameter - {", ".join(url_parameters.keys())}'
                ),
                HTTPStatus.BAD_REQUEST,
            )

    return_json_object = jsonify(data="Data (default window)")
    return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/get_weekly_amounts", methods=["GET"])
def get_weekly_amounts():
    """
    Weekly amounts endpoint.
    ---
    get:
        summary: Get weekly amounts endpoint.
        description: Get all weekly amounts.
        responses:
            200:
                description: Returns JSON object containing weekly amounts.
                schema: {"weeklyAmounts": any}
            204: Returns empty object.
    """
    database_session = db.session()
    expenses = (
        database_session.query(
            func.extract("week", Expenses.date).label("week"),
            func.extract("year", Expenses.date).label("year"),
            func.sum(Expenses.amount).label("amount"),
        )
        .group_by(
            func.extract("week", Expenses.date), func.extract("year", Expenses.date)
        )
        .order_by(func.extract("week", Expenses.date))
    )
    database_session.close()
    chosen_columns = ["week", "year", "amount"]

    expense_dict = convert_orm_object_to_dict(expenses, chosen_columns)
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response("", HTTPStatus.PARTIAL_CONTENT)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"weeklyAmounts": data_final})
    return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/get_monthly_amounts", methods=["GET"])
def get_monthly_amounts():
    """
    Monthly amounts endpoint.
    ---
    get:
        summary: Get monthly amounts endpoint.
        description: Get all monthly amounts.
        responses:
            200:
                description: Returns JSON object containing monthly amounts.
                schema: {"monthlyTransactions": any}
            204: Returns empty object.
    """
    database_session = db.session()
    expenses = (
        database_session.query(
            func.extract("month", Expenses.date).label("month"),
            func.extract("year", Expenses.date).label("year"),
            func.sum(Expenses.amount).label("amount"),
        )
        .group_by(
            func.extract("month", Expenses.date), func.extract("year", Expenses.date)
        )
        .order_by(func.extract("month", Expenses.date))
    )
    database_session.close()
    chosen_columns = ["month", "year", "amount"]
    expense_dict = convert_orm_object_to_dict(expenses, chosen_columns)
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response("", HTTPStatus.PARTIAL_CONTENT)

    expenses_df["month"] = expenses_df["month"].apply(
        lambda x: calendar.month_name[int(x)]
    )
    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_json_object = jsonify(data={"monthlyTransactions": data_final})
    return generate_response(return_json_object, HTTPStatus.OK)


@bp.route("/get_categorical_amounts", methods=["GET"])
def get_categorical_amount():
    """
    Categorical amounts endpoint.
    ---
    get:
        summary: Get categorical amounts endpoint.
        description: Get all categorical amounts.
        responses:
            200:
                description: Returns JSON object containing categorical amounts.
                schema: {"categoricalAmounts": any}
            204: Returns empty object.
    """
    database_session = db.session()
    expenses = database_session.query(
        Expenses.category, func.sum(Expenses.amount).label("amount")
    ).group_by(Expenses.category)
    database_session.close()
    expense_dict = convert_orm_object_to_dict(expenses, ["category", "amount"])
    expenses_df = pd.DataFrame.from_dict(expense_dict)

    if expenses_df.empty:
        return generate_response("", HTTPStatus.PARTIAL_CONTENT)

    data_final = json.loads(expenses_df.to_json(orient="records"))
    return_response_object = jsonify(data={"categoricalAmounts": data_final})
    return generate_response(return_response_object, HTTPStatus.OK)
