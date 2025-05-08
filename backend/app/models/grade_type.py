from app import db

class GradeType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<GradeType {self.name}>'
