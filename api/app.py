from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config='api.config.DevConfig'):
    app = Flask(__name__)

    app.config.from_object(config)

    # Registering Blueprints
    from api.expenses.endpoints import bp as expenses_blueprint
    app.register_blueprint(expenses_blueprint)

    # Registering and initialising database

    db.init_app(app)

    with app.app_context():
        db.create_all()

        return app
