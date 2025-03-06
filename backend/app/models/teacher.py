from app import db
from datetime import date

class Teacher(db.Model):
    id = db.Column(db.String(11), primary_key=True)
    identity_number = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(10), unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Teacher {self.first_name} {self.last_name}>'