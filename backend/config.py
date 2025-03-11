import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:181003@localhost/sedu"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
