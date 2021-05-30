from flask import Flask
from api.expenses.endpoints import bp


def create_app(config="api.config"):
    app = Flask(__name__)

    app.config.from_object(config)
    # Registering Blueprints
    app.register_blueprint(bp)

    return app
