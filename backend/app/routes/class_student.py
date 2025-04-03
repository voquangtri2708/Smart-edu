from flask import Blueprint, request, jsonify
from app import db
from app.models.class_student import ClassStudent
from app.models.classs import Class
from datetime import datetime

class_student_bp = Blueprint('class_student', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@class_student_bp.route('/class_students', methods=['POST'])
def create_class_student():
    data = request.get_json()
    new_class_student = ClassStudent(
        class_id=data['class_id'],
        student_id=data['student_id']
    )
    db.session.add(new_class_student)
    db.session.commit()
    return jsonify({"message": "ClassStudent created successfully"}), 201

@class_student_bp.route('/class_students', methods=['GET'])
def get_class_students():
    class_students = ClassStudent.query.all()
    return jsonify([{
        "class_id": class_student.class_id,
        "student_id": class_student.student_id
    } for class_student in class_students])

@class_student_bp.route('/class_students/<int:class_id>/<string:student_id>', methods=['GET'])
def get_class_student(class_id, student_id):
    class_student = ClassStudent.query.get_or_404((class_id, student_id))
    return jsonify({
        "class_id": class_student.class_id,
        "student_id": class_student.student_id
    })

@class_student_bp.route('/class_students/<int:class_id>/<string:student_id>', methods=['PUT'])
def update_class_student(class_id, student_id):
    data = request.get_json()
    class_student = ClassStudent.query.get_or_404((class_id, student_id))
    
    if 'class_id' in data:
        class_student.class_id = data['class_id']
    if 'student_id' in data:
        class_student.student_id = data['student_id']
    
    db.session.commit()
    return jsonify({"message": "ClassStudent updated successfully"})

@class_student_bp.route('/class_students/<int:class_id>/<string:student_id>', methods=['DELETE'])
def delete_class_student(class_id, student_id):
    class_student = ClassStudent.query.get_or_404((class_id, student_id))
    db.session.delete(class_student)
    db.session.commit()
    return jsonify({"message": "ClassStudent deleted successfully"})

@class_student_bp.route('/class_students/student/<string:student_id>/classes', methods=['GET'])
def get_classes_by_student(student_id):
    """Lấy danh sách lớp học mà học sinh đang tham gia"""
    
    class_students = ClassStudent.query.filter_by(student_id=student_id).all()
    
    classes = []
    for cs in class_students:
        class_ = Class.query.get(cs.class_id)
        if class_:
            classes.append({
                "id": class_.id,
                "code": class_.code,
                "subject_id": class_.subject_id,
                "subject_code": class_.subject_code,
                "start_date": format_date(class_.start_date),
                "end_date": format_date(class_.end_date),
                "status": class_.status
            })
    
    return jsonify(classes)