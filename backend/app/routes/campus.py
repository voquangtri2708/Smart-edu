from flask import Blueprint, request, jsonify
from app import db
from app.models.campus import Campus
from app.utils.auth import auth_required, admin_required

campus_bp = Blueprint('campus', __name__)

@campus_bp.route('/campuses', methods=['POST'])
@auth_required
@admin_required
def create_campus():
    data = request.get_json()
    new_campus = Campus(
        name=data['name'],
        address=data['address']
    )
    db.session.add(new_campus)
    db.session.commit()
    return jsonify({"message": "Campus created successfully"}), 201

@campus_bp.route('/campuses', methods=['GET'])
@auth_required
def get_campuses():
    campuses = Campus.query.all()
    return jsonify([{
        "id": campus.id,
        "name": campus.name,
        "address": campus.address
    } for campus in campuses])

@campus_bp.route('/campuses/<int:id>', methods=['GET'])
@auth_required
def get_campus(id):
    campus = Campus.query.get_or_404(id)
    return jsonify({
        "id": campus.id,
        "name": campus.name,
        "address": campus.address
    })

@campus_bp.route('/campuses/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_campus(id):
    data = request.get_json()
    campus = Campus.query.get_or_404(id)
    
    if 'name' in data:
        campus.name = data['name']
    if 'address' in data:
        campus.address = data['address']
    
    db.session.commit()
    return jsonify({"message": "Campus updated successfully"})

@campus_bp.route('/campuses/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_campus(id):
    campus = Campus.query.get_or_404(id)
    db.session.delete(campus)
    db.session.commit()
    return jsonify({"message": "Campus deleted successfully"})