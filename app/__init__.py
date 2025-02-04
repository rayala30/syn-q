from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Load the config file
    app.config.from_object(Config)

    # Initialize the app with db
    db.init_app(app)

    # Import routes and models
    from app.routes import main_bp
    app.register_blueprint(main_bp, url_prefix='/api')

    return app

