from flask import Blueprint, request, jsonify, g
from app import db
from app.models.building import Building
from app.utils.auth import auth_required, admin_required

building_bp = Blueprint('building', __name__)

@building_bp.route('/buildings', methods=['POST'])
@auth_required
@admin_required
def create_building():
    data = request.get_json()
    new_building = Building(
        name=data['name'],
        address=data['address'],
        campus_id=data['campus_id'],
        description=data.get('description')
    )
    db.session.add(new_building)
    db.session.commit()
    return jsonify({"message": "Building created successfully"}), 201

@building_bp.route('/buildings', methods=['GET'])
@auth_required
def get_buildings():
    buildings = Building.query.all()
    return jsonify([{
        "id": building.id,
        "name": building.name,
        "address": building.address,
        "campus_id": building.campus_id,
        "description": building.description
    } for building in buildings])

@building_bp.route('/buildings/<int:id>', methods=['GET'])
@auth_required
def get_building(id):
    building = Building.query.get_or_404(id)
    return jsonify({
        "id": building.id,
        "name": building.name,
        "address": building.address,
        "campus_id": building.campus_id,
        "description": building.description
    })

@building_bp.route('/buildings/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_building(id):
    data = request.get_json()
    building = Building.query.get_or_404(id)
    
    if 'name' in data:
        building.name = data['name']
    if 'address' in data:
        building.address = data['address']
    if 'campus_id' in data:
        building.campus_id = data['campus_id']
    if 'description' in data:
        building.description = data['description']
    
    db.session.commit()
    return jsonify({"message": "Building updated successfully"})

@building_bp.route('/buildings/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_building(id):
    building = Building.query.get_or_404(id)
    db.session.delete(building)
    db.session.commit()
    return jsonify({"message": "Building deleted successfully"})