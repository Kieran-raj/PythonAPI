"Module containing generaic helper functions."

from typing import Dict, List
import pandas as pd
from flask import Response, make_response


def generate_response(json_object: Response, status_code: int) -> Response:
    """
    Returns reposnse.

            Parameters:
                    json_object (Response): Data to return in reponse.
                    status_code (int): Status code for response.

            Returns:
                    reponse (Response): Reponse object.
    """
    response = make_response(json_object, status_code)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def convert_datetype_to_string(df: pd.DataFrame, date_column_name: str) -> pd.DataFrame:
    """
    Converts the date type in a pandas dataframe to a strings.

            Parameters:
                    df (pd.DataFrame): A pandas dataframe.
                    date_column_name (str): Name of the column that contains the date.

            Returns:
                    df (pd.DataFrame): Dataframe with converted date as a string.
    """

    try:
        df[date_column_name] = df[date_column_name].dt.strftime("%Y-%m-%d")
    except AttributeError:
        df[date_column_name] = df[date_column_name]
    return df


def convert_orm_object_to_dict(data, chosen_columns: List[str]) -> Dict:
    """
    Converts the orm sql object to a dictionary.

            Parameters:
                    data: Data returned from SQLAlchemy ORM query.
                    chosen_columns (List[str]): Names of columns in table.

            Returns:
                    expenses_dict (Dict):
    """
    expenses_dict = {}
    for column in chosen_columns:
        expenses_dict[column] = [expense[column] for expense in data]
    return expenses_dict
