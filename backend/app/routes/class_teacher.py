from flask import Blueprint, request, jsonify
from app import db
from app.models.class_teacher import ClassTeacher
from app.models.teacher import Teacher
from app.utils.auth import auth_required, admin_required

class_teacher_bp = Blueprint('class_teacher', __name__)

@class_teacher_bp.route('/class_teachers', methods=['POST'])
@auth_required
@admin_required
def create_class_teacher():
    data = request.get_json()
    
    # Validate input data
    if not data or 'class_id' not in data or 'teacher_id' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    # Check if the mapping already exists
    existing = ClassTeacher.query.get((data['class_id'], data['teacher_id']))
    if existing:
        return jsonify({"message": "Giảng viên đã được gán cho lớp học này"}), 409
    
    new_class_teacher = ClassTeacher(
        class_id=data['class_id'],
        teacher_id=data['teacher_id']
    )
    
    try:
        db.session.add(new_class_teacher)
        db.session.commit()
        return jsonify({"message": "ClassTeacher created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {str(e)}"}), 400

@class_teacher_bp.route('/class_teachers', methods=['GET'])
@auth_required
def get_class_teachers():
    try:
        class_teachers = ClassTeacher.query.all()
        return jsonify([{
            "class_id": class_teacher.class_id,
            "teacher_id": class_teacher.teacher_id
        } for class_teacher in class_teachers])
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['GET'])
@auth_required
def get_class_teacher(class_id, teacher_id):
    try:
        class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
        return jsonify({
            "class_id": class_teacher.class_id,
            "teacher_id": class_teacher.teacher_id
        })
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['PUT'])
@auth_required
@admin_required
def update_class_teacher(class_id, teacher_id):
    try:
        data = request.get_json()
        class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
        
        # Since the primary key is a composite, we need to handle updates carefully
        if 'class_id' in data and 'teacher_id' in data:
            # If both parts of the PK are being changed, we need to delete and recreate
            new_class_teacher = ClassTeacher(
                class_id=data['class_id'],
                teacher_id=data['teacher_id']
            )
            db.session.delete(class_teacher)
            db.session.add(new_class_teacher)
        else:
            # Handle individual field updates if needed (not likely for this model)
            if 'class_id' in data:
                return jsonify({"message": "Cannot update part of primary key separately"}), 400
            if 'teacher_id' in data:
                return jsonify({"message": "Cannot update part of primary key separately"}), 400
            
        db.session.commit()
        return jsonify({"message": "ClassTeacher updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {str(e)}"}), 400

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_class_teacher(class_id, teacher_id):
    try:
        class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
        db.session.delete(class_teacher)
        db.session.commit()
        return jsonify({"message": "ClassTeacher deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {str(e)}"}), 400

@class_teacher_bp.route('/class_teachers/<int:class_id>/teachers', methods=['GET'])
@auth_required
def get_teachers_by_class(class_id):
    try:
        class_teachers = ClassTeacher.query.filter_by(class_id=class_id).all()
        teachers = []
        for ct in class_teachers:
            teacher = Teacher.query.get(ct.teacher_id)
            if teacher:
                teachers.append({
                    "id": teacher.id,
                    "identity_number": teacher.identity_number,
                    "email": teacher.email,
                    "phone_number": teacher.phone_number,
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "birthday": teacher.birthday.isoformat() if teacher.birthday else None,
                    "address": teacher.address,
                    "gender": teacher.gender,
                    "avatar_url": teacher.avatar_url,
                    "bio": teacher.bio
                })
        return jsonify(teachers)
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500

@class_teacher_bp.route('/class_teachers/student/<string:student_id>/classes/<int:class_id>/teachers', methods=['GET'])
@auth_required
def get_teachers_for_feedback(student_id, class_id):
    """Lấy danh sách giảng viên mà học sinh có thể đánh giá"""
    from app.models.class_student import ClassStudent
    from app.models.teacher_feedback import TeacherFeedback
    
    try:
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
                        "phone_number": teacher.phone_number,
                        "avatar_url": teacher.avatar_url
                    })
        
        return jsonify(available_teachers)
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500

@class_teacher_bp.route('/class_teachers/teacher/<string:teacher_id>/classes', methods=['GET'])
@auth_required
def get_classes_by_teacher(teacher_id):
    """Lấy danh sách lớp học mà giảng viên đang dạy"""
    from app.models.classs import Class
    
    try:
        class_teachers = ClassTeacher.query.filter_by(teacher_id=teacher_id).all()
        
        classes = []
        for ct in class_teachers:
            class_ = Class.query.get(ct.class_id)
            if class_:
                classes.append({
                    "id": class_.id,
                    "code": class_.code,
                    "subject_id": class_.subject_id,
                    "subject_code": class_.subject_code,
                    "start_date": class_.start_date.isoformat() if class_.start_date else None,
                    "end_date": class_.end_date.isoformat() if class_.end_date else None,
                    "status": class_.status
                })
        
        return jsonify(classes)
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500