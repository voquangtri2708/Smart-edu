from flask import Blueprint, request, jsonify
from app import db
from app.models.classs import Class
from datetime import datetime

class_bp = Blueprint('class', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@class_bp.route('/classes', methods=['POST'])
def create_class():
    data = request.get_json()
    new_class = Class(
        id=data['id'],
        code=data['code'],
        max_student=data['max_student'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        subject_id=data['subject_id']
    )
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": "Class created successfully"}), 201

@class_bp.route('/classes', methods=['GET'])
def get_classes():
    classes = Class.query.all()
    return jsonify([{
        "id": class_.id,
        "code": class_.code,
        "max_student": class_.max_student,
        "start_date": format_date(class_.start_date),
        "end_date": format_date(class_.end_date),
        "subject_id": class_.subject_id
    } for class_ in classes])

@class_bp.route('/classes/<string:id>', methods=['GET'])
def get_class(id):
    class_ = Class.query.get_or_404(id)
    return jsonify({
        "id": class_.id,
        "code": class_.code,
        "max_student": class_.max_student,
        "start_date": format_date(class_.start_date),
        "end_date": format_date(class_.end_date),
        "subject_id": class_.subject_id
    })

@class_bp.route('/classes/<string:id>', methods=['PUT'])
def update_class(id):
    data = request.get_json()
    class_ = Class.query.get_or_404(id)
    
    if 'code' in data:
        class_.code = data['code']
    if 'max_student' in data:
        class_.max_student = data['max_student']
    if 'start_date' in data:
        class_.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        class_.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if 'subject_id' in data:
        class_.subject_id = data['subject_id']
    
    db.session.commit()
    return jsonify({"message": "Class updated successfully"})

@class_bp.route('/classes/<string:id>', methods=['DELETE'])
def delete_class(id):
    class_ = Class.query.get_or_404(id)
    db.session.delete(class_)
    db.session.commit()
    return jsonify({"message": "Class deleted successfully"})