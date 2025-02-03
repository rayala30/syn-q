import os

class Config:
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/synq_db")
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)  # Generate a random key if not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("postgresql://postgres:SbNVVTiMwUUZBgndfKFbRvtKrsOpwMCr@postgres.railway.internal:5432/railway")  # Fetch DATABASE_URL from Railway environment

