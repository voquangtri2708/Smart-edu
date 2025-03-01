from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)

    # Import và đăng ký Blueprint sau khi tạo app
    from app.routes.predict import predict_bp
    app.register_blueprint(predict_bp, url_prefix="/api")

    return app
