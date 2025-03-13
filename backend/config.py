import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:181003@localhost/sedu_v1")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
