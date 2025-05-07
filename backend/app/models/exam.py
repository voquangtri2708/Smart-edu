from app import db
from datetime import datetime

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    exam_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    grade_type_id = db.Column(db.Integer, db.ForeignKey('grade_type.id'), nullable=True)
    exam_start_time = db.Column(db.Time, nullable=False)
    exam_end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('ExamQuestion', backref='exam', cascade='all, delete-orphan')
    grade_type = db.relationship('GradeType', backref='exams')
    
    def __repr__(self):
        return f'<Exam {self.title}>' 