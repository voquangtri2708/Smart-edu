from flask import Blueprint, request, jsonify, g
from app import db
from app.models.subject import Subject
from app.utils.auth import auth_required, admin_required

subject_bp = Blueprint('subject', __name__)

@subject_bp.route('/subjects', methods=['POST'])
@auth_required
@admin_required
def create_subject():
    data = request.get_json()
    new_subject = Subject(
        code=data['code'],
        name=data['name'],
        credit=data['credit'],
        description=data.get('description')
    )
    db.session.add(new_subject)
    db.session.commit()
    return jsonify({"message": "Subject created successfully"}), 201

@subject_bp.route('/subjects', methods=['GET'])
@auth_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        "id": subject.id,
        "code": subject.code,
        "name": subject.name,
        "credit": subject.credit,
        "description": subject.description
    } for subject in subjects])

@subject_bp.route('/subjects/<int:id>', methods=['GET'])
@auth_required
def get_subject(id):
    subject = Subject.query.get_or_404(id)
    return jsonify({
        "id": subject.id,
        "code": subject.code,
        "name": subject.name,
        "credit": subject.credit,
        "description": subject.description
    })

@subject_bp.route('/subjects/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_subject(id):
    data = request.get_json()
    subject = Subject.query.get_or_404(id)
    
    if 'code' in data:
        subject.code = data['code']
    if 'name' in data:
        subject.name = data['name']
    if 'credit' in data:
        subject.credit = data['credit']
    if 'description' in data:
        subject.description = data['description']
    
    db.session.commit()
    return jsonify({"message": "Subject updated successfully"})

@subject_bp.route('/subjects/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({"message": "Subject deleted successfully"})