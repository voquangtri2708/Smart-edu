from flask import Blueprint, request, jsonify
from app import db
from app.models.building import Building

building_bp = Blueprint('building', __name__)

@building_bp.route('/buildings', methods=['POST'])
def create_building():
    data = request.get_json()
    new_building = Building(
        name=data['name'],
        campus_id=data['campus_id']
    )
    db.session.add(new_building)
    db.session.commit()
    return jsonify({"message": "Building created successfully"}), 201

@building_bp.route('/buildings', methods=['GET'])
def get_buildings():
    buildings = Building.query.all()
    return jsonify([{
        "id": building.id,
        "name": building.name,
        "campus_id": building.campus_id
    } for building in buildings])

@building_bp.route('/buildings/<int:id>', methods=['GET'])
def get_building(id):
    building = Building.query.get_or_404(id)
    return jsonify({
        "id": building.id,
        "name": building.name,
        "campus_id": building.campus_id
    })

@building_bp.route('/buildings/<int:id>', methods=['PUT'])
def update_building(id):
    data = request.get_json()
    building = Building.query.get_or_404(id)
    
    if 'name' in data:
        building.name = data['name']
    if 'campus_id' in data:
        building.campus_id = data['campus_id']
    
    db.session.commit()
    return jsonify({"message": "Building updated successfully"})

@building_bp.route('/buildings/<int:id>', methods=['DELETE'])
def delete_building(id):
    building = Building.query.get_or_404(id)
    db.session.delete(building)
    db.session.commit()
    return jsonify({"message": "Building deleted successfully"})