from flask import Blueprint, request, jsonify
from app import db
from app.models.classroom import Classroom

classroom_bp = Blueprint('classroom', __name__)

@classroom_bp.route('/classrooms', methods=['POST'])
def create_classroom():
    data = request.get_json()
    new_classroom = Classroom(
        room_number=data['room_number'],
        capacity=data['capacity'],
        building_id=data['building_id']
    )
    db.session.add(new_classroom)
    db.session.commit()
    return jsonify({"message": "Classroom created successfully"}), 201

@classroom_bp.route('/classrooms', methods=['GET'])
def get_classrooms():
    classrooms = Classroom.query.all()
    return jsonify([{
        "id": classroom.id,
        "room_number": classroom.room_number,
        "capacity": classroom.capacity,
        "building_id": classroom.building_id
    } for classroom in classrooms])

@classroom_bp.route('/classrooms/<int:id>', methods=['GET'])
def get_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    return jsonify({
        "id": classroom.id,
        "room_number": classroom.room_number,
        "capacity": classroom.capacity,
        "building_id": classroom.building_id
    })

@classroom_bp.route('/classrooms/<int:id>', methods=['PUT'])
def update_classroom(id):
    data = request.get_json()
    classroom = Classroom.query.get_or_404(id)
    
    if 'room_number' in data:
        classroom.room_number = data['room_number']
    if 'capacity' in data:
        classroom.capacity = data['capacity']
    if 'building_id' in data:
        classroom.building_id = data['building_id']
    
    db.session.commit()
    return jsonify({"message": "Classroom updated successfully"})

@classroom_bp.route('/classrooms/<int:id>', methods=['DELETE'])
def delete_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return jsonify({"message": "Classroom deleted successfully"})