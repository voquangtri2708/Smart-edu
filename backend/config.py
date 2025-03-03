import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@localhost/database_name"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
