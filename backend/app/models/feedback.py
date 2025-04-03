from app import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=True)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    teacher_id = db.Column(db.String(11), db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sentiment = db.Column(db.Enum('Tiêu cực', 'Trung lập', 'Tích cực'), default='Trung lập', nullable=False)

    def __repr__(self):
        return f'<Feedback {self.id}>'