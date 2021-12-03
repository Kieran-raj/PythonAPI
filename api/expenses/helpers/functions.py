from flask import Response, make_response

def generate_response(json_object: Response, status_code: int):
    response = make_response(json_object, status_code)
    response.headers.add( "Access-Control-Allow-Origin", "*")
    return response