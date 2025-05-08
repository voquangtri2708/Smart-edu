from app import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('PRESENT', 'ABSENT', 'EXCUSED'), nullable=False)
    recorded_by = db.Column(db.String(11), db.ForeignKey('teacher.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    ip_public = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Attendance student_id={self.student_id} class_id={self.class_id} status={self.status}>'