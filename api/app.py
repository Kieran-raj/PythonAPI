import os
from flask import Flask
from api import db
from api.expenses.endpoints import bp as expenses_blueprint


def create_app(config="api.config"):
    app = Flask(__name__)

    app.config.from_object(config)
    database_username = os.environ.get("DATABASE_USERNAME")
    database_password = os.environ.get("DATABASE_PASSWORD")
    database_ip = os.environ.get("DATABASE_IP")
    database_port = os.environ.get("DATABASE_PORT")
    database = os.environ.get("DATABASE_NAME")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{database_username}:{database_password}@{database_ip}:{database_port}/{database}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Registering Blueprints
    app.register_blueprint(expenses_blueprint)

    # Registering and initialising database

    db.init_app(app)

    return app
