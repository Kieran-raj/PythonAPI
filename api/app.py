from flask import Flask
from api.expenses.endpoints import bp


def create_app():
    app = Flask(__name__)

    # Registering Blueprints
    app.register_blueprint(bp)

    return app
