from flask import Blueprint, request, jsonify, g
from app import db
from app.models.class_student import ClassStudent
from app.models.classs import Class
from app.models.student import Student
from datetime import datetime
from app.utils.auth import auth_required, admin_required, student_self_or_admin_required

class_student_bp = Blueprint('class_student', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@class_student_bp.route('/class_students', methods=['POST'])
@auth_required
@admin_required
def create_class_student():
    data = request.get_json()
    class_id = data.get('class_id')
    student_id = data.get('student_id')
    
    if not class_id or not student_id:
        return jsonify({"message": "Thiếu thông tin class_id hoặc student_id"}), 400
    
    # Kiểm tra lớp học có tồn tại không
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404
    
    # Kiểm tra sinh viên có tồn tại không
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Sinh viên không tồn tại"}), 404
    
    # Kiểm tra sinh viên đã trong lớp chưa
    existing = ClassStudent.query.get((class_id, student_id))
    if existing:
        return jsonify({"message": "Sinh viên đã có trong lớp học này"}), 400
    
    # Kiểm tra số lượng sinh viên trong lớp học
    current_student_count = ClassStudent.query.filter_by(class_id=class_id).count()
    
    # Kiểm tra nếu đã đạt số lượng tối đa
    if current_student_count >= class_.max_student:
        return jsonify({
            "message": f"Lớp học đã đạt số lượng sinh viên tối đa ({class_.max_student} sinh viên)"
        }), 400
    
    # Thêm sinh viên vào lớp học
    new_class_student = ClassStudent(
        class_id=class_id,
        student_id=student_id
    )
    db.session.add(new_class_student)
    db.session.commit()
    return jsonify({"message": "Đã thêm sinh viên vào lớp học thành công"}), 201

@class_student_bp.route('/class_students', methods=['GET'])
@auth_required
@admin_required
def get_class_students():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    class_id = request.args.get('class_id')
    student_id = request.args.get('student_id')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Build query with filters
    query = ClassStudent.query
    
    if class_id:
        query = query.filter(ClassStudent.class_id == class_id)
    if student_id:
        query = query.filter(ClassStudent.student_id.ilike(f'%{student_id}%'))
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    class_students = pagination.items
    
    return jsonify({
        'items': [{
            "class_id": class_student.class_id,
            "student_id": class_student.student_id
        } for class_student in class_students],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@class_student_bp.route('/class_students/<int:class_id>/<string:student_id>', methods=['GET'])
@auth_required
def get_class_student(class_id, student_id):
    # Kiểm tra quyền: admin hoặc student đang xem thông tin của chính mình
    if not g.is_admin and g.student_id != student_id:
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    
    class_student = ClassStudent.query.get_or_404((class_id, student_id))
    return jsonify({
        "class_id": class_student.class_id,
        "student_id": class_student.student_id
    })

@class_student_bp.route('/class_students/<int:class_id>/<string:student_id>', methods=['PUT'])
@auth_required
@admin_required
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
@auth_required
@admin_required
def delete_class_student(class_id, student_id):
    class_student = ClassStudent.query.get_or_404((class_id, student_id))
    db.session.delete(class_student)
    db.session.commit()
    return jsonify({"message": "ClassStudent deleted successfully"})

@class_student_bp.route('/class_students/student/<string:student_id>/classes', methods=['GET'])
@auth_required
def get_classes_by_student(student_id):
    """Lấy danh sách lớp học mà học sinh đang tham gia"""
    
    # Kiểm tra quyền: admin hoặc student đang xem thông tin của chính mình
    if not g.is_admin and g.student_id != student_id:
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Get the class IDs for this student
    class_student_query = ClassStudent.query.filter_by(student_id=student_id)
    class_ids = [cs.class_id for cs in class_student_query.all()]
    
    if not class_ids:
        return jsonify({
            'items': [],
            'pagination': {
                'total': 0,
                'pages': 0,
                'page': page,
                'per_page': per_page,
                'has_next': False,
                'has_prev': False
            }
        })
    
    # Query classes with these IDs
    query = Class.query.filter(Class.id.in_(class_ids))
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(Class.code.ilike(f'%{search_query}%'))
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    classes = pagination.items
    
    return jsonify({
        'items': [{
            "id": class_.id,
            "code": class_.code,
            "subject_id": class_.subject_id,
            "subject_code": class_.subject_code if hasattr(class_, 'subject_code') else None,
            "start_date": format_date(class_.start_date),
            "end_date": format_date(class_.end_date),
            "status": class_.status if hasattr(class_, 'status') else None
        } for class_ in classes],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@class_student_bp.route('/class_students/class/<int:class_id>/students', methods=['GET'])
@auth_required
def get_students_by_class(class_id):
    """Lấy danh sách học sinh tham gia lớp học"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Get the student IDs for this class
    class_student_query = ClassStudent.query.filter_by(class_id=class_id)
    student_ids = [cs.student_id for cs in class_student_query.all()]
    
    if not student_ids:
        return jsonify({
            'items': [],
            'pagination': {
                'total': 0,
                'pages': 0,
                'page': page,
                'per_page': per_page,
                'has_next': False,
                'has_prev': False
            }
        })
    
    # Query students with these IDs
    query = Student.query.filter(Student.id.in_(student_ids))
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (Student.id.ilike(f'%{search_query}%')) |
            (Student.first_name.ilike(f'%{search_query}%')) |
            (Student.last_name.ilike(f'%{search_query}%'))
        )
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    
    return jsonify({
        'items': [{
            'id': student.id,
            'identity_number': student.identity_number,
            'email': student.email,
            'phone_number': student.phone_number,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'birthday': student.birthday.isoformat() if student.birthday else None,
            'gender': student.gender
        } for student in students],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })