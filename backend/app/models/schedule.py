from app import db
from datetime import datetime, time, date

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    day_of_week = db.Column(db.Enum('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    specific_date = db.Column(db.Date, nullable=True)
    
    # Define relationships
    class_ = db.relationship('Class', backref=db.backref('schedules', lazy=True))
    classroom = db.relationship('Classroom', backref=db.backref('schedules', lazy=True))
    
    def __repr__(self):
        return f'<Schedule {self.id} for Class {self.class_id}>' 