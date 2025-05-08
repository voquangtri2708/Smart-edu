from app import db
from datetime import datetime, time, date

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    specific_date = db.Column(db.Date, nullable=False)
    day_of_week = db.Column(db.Enum('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), nullable=False)
    
    # Define relationships
    class_ = db.relationship('Class', backref=db.backref('schedules', lazy=True))
    classroom = db.relationship('Classroom', backref=db.backref('schedules', lazy=True))
    
    def __repr__(self):
        return f'<Schedule {self.id} for Class {self.class_id}>'
    
    # Tự động tính day_of_week từ specific_date
    def calculate_day_of_week(self):
        if self.specific_date:
            # Python sử dụng 0 = Monday, 6 = Sunday
            # Chuyển đổi thành enum MON, TUE, ...
            day_map = {
                0: 'MON',
                1: 'TUE',
                2: 'WED',
                3: 'THU',
                4: 'FRI',
                5: 'SAT',
                6: 'SUN'
            }
            return day_map[self.specific_date.weekday()]
        return None
    
    def before_save(self):
        # Tự động cập nhật day_of_week trước khi lưu
        self.day_of_week = self.calculate_day_of_week() 