from flask import Blueprint, request, jsonify
from app import db
from app.models.class_teacher import ClassTeacher
from app.models.teacher import Teacher

class_teacher_bp = Blueprint('class_teacher', __name__)

@class_teacher_bp.route('/class_teachers', methods=['POST'])
def create_class_teacher():
    data = request.get_json()
    new_class_teacher = ClassTeacher(
        class_id=data['class_id'],
        teacher_id=data['teacher_id']
    )
    db.session.add(new_class_teacher)
    db.session.commit()
    return jsonify({"message": "ClassTeacher created successfully"}), 201

@class_teacher_bp.route('/class_teachers', methods=['GET'])
def get_class_teachers():
    class_teachers = ClassTeacher.query.all()
    return jsonify([{
        "class_id": class_teacher.class_id,
        "teacher_id": class_teacher.teacher_id
    } for class_teacher in class_teachers])

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['GET'])
def get_class_teacher(class_id, teacher_id):
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    return jsonify({
        "class_id": class_teacher.class_id,
        "teacher_id": class_teacher.teacher_id
    })

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['PUT'])
def update_class_teacher(class_id, teacher_id):
    data = request.get_json()
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    
    if 'class_id' in data:
        class_teacher.class_id = data['class_id']
    if 'teacher_id' in data:
        class_teacher.teacher_id = data['teacher_id']
    
    db.session.commit()
    return jsonify({"message": "ClassTeacher updated successfully"})

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['DELETE'])
def delete_class_teacher(class_id, teacher_id):
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    db.session.delete(class_teacher)
    db.session.commit()
    return jsonify({"message": "ClassTeacher deleted successfully"})

@class_teacher_bp.route('/class_teachers/<int:class_id>/teachers', methods=['GET'])
def get_teachers_by_class(class_id):
    class_teachers = ClassTeacher.query.filter_by(class_id=class_id).all()
    teachers = [Teacher.query.get(ct.teacher_id) for ct in class_teachers]
    return jsonify([{
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "email": teacher.email,
        "phone_number": teacher.phone_number
    } for teacher in teachers])