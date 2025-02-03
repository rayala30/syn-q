import os

class Config:
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/synq_db")
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)  # Generate a random key if not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set!")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

