from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Connecting to database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    
    # Sửa cấu hình CORS
    # Xác định cụ thể các methods và headers được phép
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*", 
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "expose_headers": ["Content-Length", "Content-Type"],
             "supports_credentials": True,
             "max_age": 600
         }})

    # Import và đăng ký Blueprint sau khi tạo app
    from app.routes.account import account_bp
    from app.routes.classs import class_bp
    from app.routes.class_student import class_student_bp
    from app.routes.class_teacher import class_teacher_bp
    from app.routes.student import student_bp
    from app.routes.subject import subject_bp
    from app.routes.teacher import teacher_bp
    from app.routes.campus import campus_bp
    from app.routes.building import building_bp
    from app.routes.classroom import classroom_bp
    from app.routes.feedback_availability import feedback_availability_bp
    from app.routes.feedback import feedback_bp
    from app.routes.avatar import avatar_bp
    from app.routes.grade_type import grade_type_bp
    from app.routes.schedule import schedule_bp
    from app.routes.attendance import attendance_bp
    from app.routes.grade import grade_bp
    from app.routes.exam import exam_bp
    from app.routes.notification import notification_bp

    app.register_blueprint(account_bp, url_prefix="/api")
    app.register_blueprint(class_bp, url_prefix="/api")
    app.register_blueprint(class_student_bp, url_prefix="/api")
    app.register_blueprint(class_teacher_bp, url_prefix="/api")
    app.register_blueprint(student_bp, url_prefix="/api")
    app.register_blueprint(subject_bp, url_prefix="/api")
    app.register_blueprint(teacher_bp, url_prefix="/api")
    app.register_blueprint(campus_bp, url_prefix="/api")
    app.register_blueprint(building_bp, url_prefix="/api")
    app.register_blueprint(classroom_bp, url_prefix="/api")
    app.register_blueprint(feedback_availability_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(avatar_bp, url_prefix="/api")
    app.register_blueprint(grade_type_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix="/api")
    app.register_blueprint(grade_bp, url_prefix="/api")
    app.register_blueprint(notification_bp, url_prefix="/api")
    
    return app