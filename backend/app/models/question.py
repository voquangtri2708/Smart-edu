from app import db
from datetime import datetime

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('MULTIPLE_CHOICE', 'TRUE_FALSE', 'ESSAY', 'SHORT_ANSWER'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', cascade='all, delete-orphan')
    exam_questions = db.relationship('ExamQuestion', backref='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}>' 