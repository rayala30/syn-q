from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Load the config file
    # app.config.from_object("app.config.Config")
    app.config.from_object(Config)

    # Initialize the app with db
    db.init_app(app)

    # Import routes and models
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

