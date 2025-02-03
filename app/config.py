import os

class Config:
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/synq_db")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)  # Generate a random key if not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    print(f"DATABASE_URL: {DATABASE_URL}")  # Add this line to debug
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "postgresql://localhost/synq_db"  # Default fallback

