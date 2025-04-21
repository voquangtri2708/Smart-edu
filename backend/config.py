import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database config using individual parameters
    DB_HOST = os.environ.get("HOST")
    DB_USER = os.environ.get("USER")
    DB_PASSWORD = os.environ.get("PASSWORD")
    DB_NAME = os.environ.get("DATABASE")
    
    # Build the SQLAlchemy URI from individual parameters
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other configurations
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    
    # Cloudinary config
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
