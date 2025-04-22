from app import db
from datetime import datetime, time

class Schedule(db.Model):
    __tablename__ = 'schedule'  # Tên bảng giống như trong SQL
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.Enum('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), nullable=False)
    specific_date = db.Column(db.Date)
    
    # Khóa ngoại
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    
    # Relationships
    class_info = db.relationship('Class', backref='schedules')
    classroom = db.relationship('Classroom', backref='schedules')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'day_of_week': self.day_of_week,
            'specific_date': self.specific_date.strftime('%Y-%m-%d') if self.specific_date else None,
            'class_id': self.class_id,
            'classroom_id': self.classroom_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_relations:
            result['class_info'] = self.class_info.to_dict(False) if self.class_info else None
            result['classroom'] = self.classroom.to_dict(False) if self.classroom else None
            
        return result