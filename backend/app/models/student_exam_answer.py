from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class StudentExamAnswer(db.Model):
    """
    Model for storing student answers for exam questions
    """
    __tablename__ = 'student_exam_answer'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to ensure a student can only answer a question once per exam
    __table_args__ = (
        UniqueConstraint('student_id', 'exam_id', 'question_id', name='unique_student_exam_question'),
    )
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('exam_answers', lazy=True))
    exam = db.relationship('Exam', backref=db.backref('student_answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('student_answers', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'exam_id': self.exam_id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'is_correct': self.is_correct,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<StudentExamAnswer {self.id}>' 