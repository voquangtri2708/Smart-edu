from app import db
from datetime import datetime, timedelta

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=False)
    teacher_id = db.Column(db.String(11), db.ForeignKey('teacher.id'), nullable=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sentiment = db.Column(db.Enum('POSITIVE', 'NEUTRAL', 'NEGATIVE'), nullable=False)
    feedback_type = db.Column(db.Enum('CLASSROOM', 'TEACHER'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback {self.id}>'
    
    def set_dates(self, class_start_date, class_end_date):
        self.start_date = class_start_date
        self.end_date = class_end_date + timedelta(days=7)