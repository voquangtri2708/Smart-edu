from app import db

class ClassStudent(db.Model):
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    student_id = db.Column(db.String(11), db.ForeignKey('student.id'), primary_key=True)

    def __repr__(self):
        return f'<ClassStudent class_id={self.class_id} student_id={self.student_id}>'