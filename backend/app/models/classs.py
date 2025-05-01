from app import db
from datetime import date

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    max_student = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    def __repr__(self):
        return f'<Class {self.code}>'