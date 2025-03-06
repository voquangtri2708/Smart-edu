from app import db

class Class(db.Model):
    id = db.Column(db.String(11), primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    max_student = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    def __repr__(self):
        return f'<Class {self.code}>'