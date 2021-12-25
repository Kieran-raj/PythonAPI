import pandas as pd
from flask import Response, make_response

def generate_response(json_object: Response, status_code: int):
    response = make_response(json_object, status_code)
    response.headers.add( "Access-Control-Allow-Origin", "*")
    return response

def convert_datetype_to_string(
    df: pd.DataFrame, date_column_name: str
    ) -> pd.DataFrame:
    try:
        df[date_column_name] = df[date_column_name].dt.strftime('%Y-%m-%d')
    except AttributeError:
        df[date_column_name] = df[date_column_name]
    return df