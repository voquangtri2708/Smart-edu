from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    # Import và đăng ký Blueprint sau khi tạo app
    from app.routes.predict import predict_bp
    from app.routes.account import account_bp
    from app.routes.classs import class_bp
    from app.routes.class_student import class_student_bp
    from app.routes.student import student_bp
    from app.routes.subject import subject_bp
    from app.routes.teacher import teacher_bp
    from app.routes.campus import campus_bp
    from app.routes.building import building_bp
    from app.routes.classroom import classroom_bp
    from app.routes.feedback import feedback_bp
    from app.routes.class_teacher import class_teacher_bp

    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(account_bp, url_prefix="/api")
    app.register_blueprint(class_bp, url_prefix="/api")
    app.register_blueprint(class_student_bp, url_prefix="/api")
    app.register_blueprint(student_bp, url_prefix="/api")
    app.register_blueprint(subject_bp, url_prefix="/api")
    app.register_blueprint(teacher_bp, url_prefix="/api")
    app.register_blueprint(campus_bp, url_prefix="/api")
    app.register_blueprint(building_bp, url_prefix="/api")
    app.register_blueprint(classroom_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(class_teacher_bp, url_prefix="/api")

    return app