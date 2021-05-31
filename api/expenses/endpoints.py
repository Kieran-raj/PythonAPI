from flask import Blueprint, current_app as app, request, render_template
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('welcome_page.html')


@bp.route('/data_base')
def test():
    result = db.engine.execute("show tables;")
    for i in result:
        print(i)
    return {"message": 200}


@bp.route('/enter_data', methods=['GET', 'POST'])
def enter_expense():
    if request.method == 'GET':
        return render_template('enter_data.html')
