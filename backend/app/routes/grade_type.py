from flask import Blueprint, request, jsonify, g
from app import db
from app.models.grade_type import GradeType
from app.models.class_teacher import ClassTeacher
from app.models.classs import Class
from datetime import datetime
from app.utils.auth import admin_required, auth_required, teacher_or_admin_required

grade_type_bp = Blueprint('grade_type', __name__)

@grade_type_bp.route('/grade_types', methods=['POST'])
@teacher_or_admin_required  # Cho phép admin và giáo viên tạo grade type
def create_grade_type():
    data = request.get_json()
    
    # Kiểm tra quyền truy cập cho giáo viên thêm vào đây nếu cần
    if g.role == 'teacher':
        # Kiểm tra xem class_id được cung cấp hay không
        class_id = data.get('class_id')
        
        if not class_id:
            return jsonify({"message": "Thiếu thông tin lớp học"}), 400
        
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền thao tác với lớp học này"}), 403
    
    new_grade_type = GradeType(
        name=data['name'],
        weight=data['weight'],
        description=data.get('description'),
        subject_id=data['subject_id']
    )
    db.session.add(new_grade_type)
    db.session.commit()
    return jsonify({"message": "Grade type created successfully", "id": new_grade_type.id}), 201

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
@teacher_or_admin_required  # Cho phép admin và giáo viên cập nhật
def update_grade_type(id):
    data = request.get_json()
    grade_type = GradeType.query.get_or_404(id)
    
    # Nếu là giáo viên, kiểm tra xem grade_type này có thuộc về lớp mà họ đang dạy không
    if g.role == 'teacher':
        # Lấy danh sách lớp học mà giáo viên đang dạy
        classes_taught = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        classes_taught = [cls[0] for cls in classes_taught]
        
        # Kiểm tra xem grade_type này có được sử dụng trong lớp mà giáo viên dạy không
        exams_using_grade_type = db.session.query(db.exists().where(
            db.and_(
                db.text('exam.grade_type_id = :grade_type_id'),
                db.text('exam.class_id IN :classes')
            )
        )).params(grade_type_id=id, classes=tuple(classes_taught) if classes_taught else (-1,)).scalar()
        
        if not exams_using_grade_type:
            return jsonify({"message": "Bạn không có quyền cập nhật loại điểm này"}), 403
    
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
@teacher_or_admin_required  # Cho phép admin và giáo viên xóa
def delete_grade_type(id):
    grade_type = GradeType.query.get_or_404(id)
    
    # Nếu là giáo viên, kiểm tra xem grade_type này có thuộc về lớp mà họ đang dạy không
    if g.role == 'teacher':
        # Lấy danh sách lớp học mà giáo viên đang dạy
        classes_taught = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        classes_taught = [cls[0] for cls in classes_taught]
        
        # Kiểm tra xem grade_type này có được sử dụng trong lớp mà giáo viên dạy không
        exams_using_grade_type = db.session.query(db.exists().where(
            db.and_(
                db.text('exam.grade_type_id = :grade_type_id'),
                db.text('exam.class_id IN :classes')
            )
        )).params(grade_type_id=id, classes=tuple(classes_taught) if classes_taught else (-1,)).scalar()
        
        if not exams_using_grade_type:
            return jsonify({"message": "Bạn không có quyền xóa loại điểm này"}), 403
    
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

# API lấy loại điểm theo lớp học
@grade_type_bp.route('/classes/<int:class_id>/grade_types', methods=['GET'])
@auth_required
def get_grade_types_by_class(class_id):
    # Lấy subject_id từ class
    class_obj = Class.query.get_or_404(class_id)
    subject_id = class_obj.subject_id
    
    # Lấy grade_types theo subject_id
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
