from app import db
from datetime import datetime

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(255), nullable=False)  # Mật khẩu đã hash (Bcrypt)
    role = db.Column(db.Enum('admin', 'student', 'teacher'), nullable=False)  # Quyền tài khoản
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=True)  # Chỉ dùng nếu là sinh viên
    teacher_id = db.Column(db.String(11), db.ForeignKey('teacher.id'), nullable=True)  # Chỉ dùng nếu là giáo viên
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # 1 = Active, 0 = Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Account {self.username}>'