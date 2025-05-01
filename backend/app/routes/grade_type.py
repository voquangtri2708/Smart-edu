from flask import Blueprint, request, jsonify
from app import db
from app.models.grade_type import GradeType
from datetime import datetime
from app.routes.account import admin_required, auth_required

grade_type_bp = Blueprint('grade_type', __name__)

@grade_type_bp.route('/grade_types', methods=['POST'])
@admin_required  # Chỉ admin mới được tạo grade type mới
def create_grade_type():
    data = request.get_json()
    new_grade_type = GradeType(
        name=data['name'],
        weight=data['weight'],
        description=data.get('description'),
        subject_id=data['subject_id']
    )
    db.session.add(new_grade_type)
    db.session.commit()
    return jsonify({"message": "Grade type created successfully"}), 201

@grade_type_bp.route('/grade_types', methods=['GET'])
@auth_required  # Người dùng đã đăng nhập mới xem được
def get_grade_types():
    grade_types = GradeType.query.all()
    return jsonify([{
        "id": grade_type.id,
        "name": grade_type.name,
        "weight": grade_type.weight,
        "description": grade_type.description,
        "subject_id": grade_type.subject_id,
        "created_at": grade_type.created_at,
        "updated_at": grade_type.updated_at
    } for grade_type in grade_types])

@grade_type_bp.route('/grade_types/<int:id>', methods=['GET'])
@auth_required # Người dùng đã đăng nhập mới xem được
def get_grade_type(id):
    grade_type = GradeType.query.get_or_404(id)
    return jsonify({
        "id": grade_type.id,
        "name": grade_type.name,
        "weight": grade_type.weight,
        "description": grade_type.description,
        "subject_id": grade_type.subject_id,
        "created_at": grade_type.created_at,
        "updated_at": grade_type.updated_at
    })

@grade_type_bp.route('/grade_types/<int:id>', methods=['PUT'])
@admin_required # Chỉ admin mới được cập nhật
def update_grade_type(id):
    data = request.get_json()
    grade_type = GradeType.query.get_or_404(id)
    
    if 'name' in data:
        grade_type.name = data['name']
    if 'weight' in data:
        grade_type.weight = data['weight']
    if 'description' in data:
        grade_type.description = data['description']
    if 'subject_id' in data:
        grade_type.subject_id = data['subject_id']
    
    db.session.commit()
    return jsonify({"message": "Grade type updated successfully"})

@grade_type_bp.route('/grade_types/<int:id>', methods=['DELETE'])
@admin_required # Chỉ admin mới được xóa
def delete_grade_type(id):
    grade_type = GradeType.query.get_or_404(id)
    db.session.delete(grade_type)
    db.session.commit()
    return jsonify({"message": "Grade type deleted successfully"})

@grade_type_bp.route('/subjects/<int:subject_id>/grade_types', methods=['GET'])
@auth_required # Người dùng đã đăng nhập mới xem được
def get_grade_types_by_subject(subject_id):
    grade_types = GradeType.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        "id": grade_type.id,
        "name": grade_type.name,
        "weight": grade_type.weight,
        "description": grade_type.description,
        "subject_id": grade_type.subject_id,
        "created_at": grade_type.created_at,
        "updated_at": grade_type.updated_at
    } for grade_type in grade_types])
