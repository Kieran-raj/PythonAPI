import pandas as pd
from typing import List
from flask import Response, make_response


def generate_response(json_object: Response, status_code: int):
    response = make_response(json_object, status_code)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def convert_datetype_to_string(df: pd.DataFrame, date_column_name: str) -> pd.DataFrame:
    try:
        df[date_column_name] = df[date_column_name].dt.strftime('%Y-%m-%d')
    except AttributeError:
        df[date_column_name] = df[date_column_name]
    return df


def convert_orm_object_to_dict(data, chosen_columns: List[str]):
    expenses_dict = {}
    for column in chosen_columns:
        expenses_dict[column] = [expense[column] for expense in data]
    return expenses_dict
