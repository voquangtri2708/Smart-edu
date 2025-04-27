from app import db

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    # address = db.Column(db.String(255), nullable=False)  # Removed because it doesn't exist in database
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)

    def __repr__(self):
        return f'<Building {self.name}>'