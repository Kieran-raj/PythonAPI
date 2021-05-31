from flask import Blueprint, current_app as app, request, render_template
from api import db
from api.templates import *

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('welcome_page.html'), 200


@bp.route('/test_data', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        result = db.engine.execute("select * from test_table;")
        return render_template('test_data.html', data=result), 200
    elif request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        print(first_name, last_name)
        return {"message": "data collected"}, 200


@bp.route('/enter_data', methods=['GET', 'POST'])
def enter_expense():
    if request.method == 'GET':
        return render_template('enter_data.html'), 200
