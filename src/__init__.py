from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    from src.routes.query_route import query_bp

    app.register_blueprint(query_bp)
    return app
