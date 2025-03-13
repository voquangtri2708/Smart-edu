from app import db
from datetime import datetime, timedelta

class TeacherFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=True)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.String(11), db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    sentiment = db.Column(db.Enum('negative', 'neutral', 'positive'), default='neutral', nullable=False)

    def __repr__(self):
        return f'<TeacherFeedback {self.id}>'

    def set_dates(self, class_start_date, class_end_date):
        self.start_date = class_start_date
        self.end_date = class_end_date + timedelta(days=7)