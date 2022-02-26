from flask import Flask
from api import db
from api.expenses.endpoints import bp as expenses_blueprint


def create_app(config='api.config.DevConfig'):
    app = Flask(__name__)

    app.config.from_object(config)

    # Registering Blueprints
    app.register_blueprint(expenses_blueprint)

    # Registering and initialising database

    db.init_app(app)

    with app.app_context():
        from api.expenses import endpoints

        db.create_all()

        return app
