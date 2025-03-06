from app import db

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)

    def __repr__(self):
        return f'<Classroom {self.room_number}>'