from flask import Blueprint, request, jsonify, g
from app import db
from app.models.class_teacher import ClassTeacher
from app.models.classs import Class
from app.models.teacher import Teacher
from app.utils.auth import auth_required, admin_required, teacher_self_or_admin_required

class_teacher_bp = Blueprint('class_teacher', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@class_teacher_bp.route('/class_teachers', methods=['POST'])
@auth_required
@admin_required
def create_class_teacher():
    data = request.get_json()
    class_id = data.get('class_id')
    teacher_id = data.get('teacher_id')
    
    if not class_id or not teacher_id:
        return jsonify({"message": "Thiếu thông tin class_id hoặc teacher_id"}), 400
    
    # Kiểm tra lớp học có tồn tại không
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404
    
    # Kiểm tra giáo viên có tồn tại không
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Giáo viên không tồn tại"}), 404
    
    # Kiểm tra giáo viên đã dạy lớp này chưa
    existing = ClassTeacher.query.get((class_id, teacher_id))
    if existing:
        return jsonify({"message": "Giáo viên đã được phân công giảng dạy lớp học này"}), 400
    
    # Thêm giáo viên vào lớp học
    new_class_teacher = ClassTeacher(
        class_id=class_id,
        teacher_id=teacher_id
    )
    
    try:
        db.session.add(new_class_teacher)
        db.session.commit()
        return jsonify({"message": "Đã thêm giáo viên vào lớp học thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {str(e)}"}), 400

@class_teacher_bp.route('/class_teachers', methods=['GET'])
@auth_required
def get_class_teachers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Build query with filters
    query = ClassTeacher.query
    
    if class_id:
        query = query.filter(ClassTeacher.class_id == class_id)
    if teacher_id:
        query = query.filter(ClassTeacher.teacher_id.ilike(f'%{teacher_id}%'))
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    class_teachers = pagination.items
    
    return jsonify({
        'items': [{
            "class_id": class_teacher.class_id,
            "teacher_id": class_teacher.teacher_id
        } for class_teacher in class_teachers],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['GET'])
@auth_required
def get_class_teacher(class_id, teacher_id):
    # Kiểm tra quyền: admin hoặc teacher đang xem thông tin của chính mình
    if not g.is_admin and g.teacher_id != teacher_id:
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    return jsonify({
        "class_id": class_teacher.class_id,
        "teacher_id": class_teacher.teacher_id
    })

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['PUT'])
@auth_required
@admin_required
def update_class_teacher(class_id, teacher_id):
    data = request.get_json()
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    
    if 'class_id' in data:
        class_teacher.class_id = data['class_id']
    if 'teacher_id' in data:
        class_teacher.teacher_id = data['teacher_id']
    
    db.session.commit()
    return jsonify({"message": "Cập nhật phân công giáo viên thành công"})

@class_teacher_bp.route('/class_teachers/<int:class_id>/<string:teacher_id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_class_teacher(class_id, teacher_id):
    class_teacher = ClassTeacher.query.get_or_404((class_id, teacher_id))
    db.session.delete(class_teacher)
    db.session.commit()
    return jsonify({"message": "Đã xóa phân công giáo viên thành công"})

@class_teacher_bp.route('/class_teachers/teacher/<string:teacher_id>/classes', methods=['GET'])
@auth_required
def get_classes_by_teacher(teacher_id):
    """Lấy danh sách lớp học mà giáo viên đang giảng dạy"""
    
    # Kiểm tra quyền: admin hoặc teacher đang xem thông tin của chính mình
    if not g.is_admin and g.teacher_id != teacher_id:
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Get the class IDs for this teacher
    class_teacher_query = ClassTeacher.query.filter_by(teacher_id=teacher_id)
    class_ids = [ct.class_id for ct in class_teacher_query.all()]
    
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
            "subject_code": class_.subject.code if hasattr(class_, 'subject') and class_.subject else None,
            "subject_name": class_.subject.name if hasattr(class_, 'subject') and class_.subject else None,
            "start_date": format_date(class_.start_date),
            "end_date": format_date(class_.end_date),
            "max_student": class_.max_student,
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

@class_teacher_bp.route('/class_teachers/class/<int:class_id>/teachers', methods=['GET'])
@auth_required
def get_teachers_by_class(class_id):
    """Lấy danh sách giáo viên giảng dạy lớp học"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Get the teacher IDs for this class
    class_teacher_query = ClassTeacher.query.filter_by(class_id=class_id)
    teacher_ids = [ct.teacher_id for ct in class_teacher_query.all()]
    
    if not teacher_ids:
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
    
    # Query teachers with these IDs
    query = Teacher.query.filter(Teacher.id.in_(teacher_ids))
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (Teacher.id.ilike(f'%{search_query}%')) |
            (Teacher.first_name.ilike(f'%{search_query}%')) |
            (Teacher.last_name.ilike(f'%{search_query}%'))
        )
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    teachers = pagination.items
    
    return jsonify({
        'items': [{
            'id': teacher.id,
            'identity_number': teacher.identity_number,
            'email': teacher.email,
            'phone_number': teacher.phone_number,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'birthday': teacher.birthday.isoformat() if teacher.birthday else None,
            'gender': teacher.gender,
            'address': teacher.address,
            'avatar_url': teacher.avatar_url,
            'bio': teacher.bio
        } for teacher in teachers],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@class_teacher_bp.route('/class_teachers/student/<string:student_id>/classes/<int:class_id>/teachers', methods=['GET'])
@auth_required
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
                    "phone_number": teacher.phone_number,
                    "avatar_url": teacher.avatar_url
                })
    
    return jsonify(available_teachers)