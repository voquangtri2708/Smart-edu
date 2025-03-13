from app import db
from datetime import date

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    max_student = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject_code = db.Column(db.String(10), db.ForeignKey('subject.code'), nullable=False)
    status = db.Column(db.Enum('pending', 'ongoing', 'completed', 'cancelled'), default='pending')

    def __repr__(self):
        return f'<Class {self.code}>'