from app import db

class ClassTeacher(db.Model):
    class_id = db.Column(db.String(11), db.ForeignKey('class.id'), primary_key=True)
    teacher_id = db.Column(db.String(11), db.ForeignKey('teacher.id'), primary_key=True)

    def __repr__(self):
        return f'<ClassTeacher class_id={self.class_id} teacher_id={self.teacher_id}>'