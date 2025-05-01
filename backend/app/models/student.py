from app import db
from datetime import date

class Student(db.Model):
    id = db.Column(db.String(11), primary_key=True)
    identity_number = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(10), unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), default=None)
    gender = db.Column(db.Enum('MALE', 'FEMALE', name='gender_enum'), nullable=False, default='MALE')
    face_encoding = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'