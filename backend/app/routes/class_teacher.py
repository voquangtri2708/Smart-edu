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

# Thêm route mới để lấy danh sách giảng viên có thể đánh giá
@class_teacher_bp.route('/class_teachers/student/<string:student_id>/classes/<int:class_id>/teachers', methods=['GET'])
def get_teachers_for_feedback(student_id, class_id):
    """Lấy danh sách giảng viên mà học sinh có thể đánh giá"""
    from app.models.class_student import ClassStudent
    from app.models.teacher_feedback import TeacherFeedback
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
        
    # Lấy tất cả giảng viên dạy lớp này
    class_teachers = ClassTeacher.query.filter_by(class_id=class_id).all()
    
    # Lấy danh sách giảng viên đã được đánh giá bởi học sinh này trong lớp này
    evaluated_teachers = db.session.query(TeacherFeedback.teacher_id).filter_by(
        student_id=student_id,
        class_id=class_id
    ).all()
    
    evaluated_teacher_ids = [t.teacher_id for t in evaluated_teachers]
    
    # Lọc ra các giảng viên chưa được đánh giá
    available_teachers = []
    
    for ct in class_teachers:
        if ct.teacher_id not in evaluated_teacher_ids:
            teacher = Teacher.query.get(ct.teacher_id)
            if teacher:
                available_teachers.append({
                    "id": teacher.id,
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "email": teacher.email,
                    "phone_number": teacher.phone_number
                })
    
    return jsonify(available_teachers)