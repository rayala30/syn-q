import os

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') # Use Railway environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Use Railway's DATABASE_URL

