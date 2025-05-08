from flask import Blueprint, request, jsonify, g
from app import db
from app.models.classs import Class
from app.utils.auth import auth_required, admin_required
from datetime import datetime, date

class_bp = Blueprint('class', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

def update_class_status(class_obj):
    """Kiểm tra và cập nhật trạng thái is_del của một lớp học dựa trên ngày kết thúc"""
    today = date.today()
    if class_obj.end_date < today and not class_obj.is_del:
        class_obj.is_del = True
        return True
    return False

def update_all_classes_status():
    """Cập nhật trạng thái is_del cho tất cả các lớp đã kết thúc"""
    today = date.today()
    expired_classes = Class.query.filter(Class.end_date < today, Class.is_del == False).all()
    if expired_classes:
        for class_obj in expired_classes:
            class_obj.is_del = True
        db.session.commit()

@class_bp.route('/classes', methods=['POST'])
@auth_required
@admin_required
def create_class():
    data = request.get_json()
    
    # Parse dates
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    # Validate end_date is after start_date
    if end_date <= start_date:
        return jsonify({"error": "Ngày kết thúc phải sau ngày bắt đầu"}), 400
    
    # Kiểm tra ngày kết thúc so với ngày hiện tại
    is_del = end_date < date.today()
    
    new_class = Class(
        code=data['code'],
        max_student=data['max_student'],
        start_date=start_date,
        end_date=end_date,
        subject_id=data.get('subject_id'),  # Changed to get with default None since it's nullable
        is_del=is_del  # Tự động đặt is_del = True nếu ngày kết thúc đã qua
    )
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": "Class created successfully"}), 201

@class_bp.route('/classes', methods=['GET'])
@auth_required
def get_classes():
    # Trước khi truy vấn, cập nhật trạng thái của tất cả các lớp
    update_all_classes_status()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Filter classes based on search query
    query = Class.query
    if search_query:
        query = query.filter(
            # Search by code
            (Class.code.ilike(f'%{search_query}%'))
        )
    
    # Lọc theo trạng thái is_del
    if not include_deleted:
        query = query.filter(Class.is_del == False)
    
    # Apply pagination to the filtered query
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    classes = pagination.items
    
    return jsonify({
        'items': [{
            "id": class_.id,
            "code": class_.code,
            "max_student": class_.max_student,
            "start_date": format_date(class_.start_date),
            "end_date": format_date(class_.end_date),
            "subject_id": class_.subject_id,
            "is_del": class_.is_del
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

@class_bp.route('/classes/<int:id>', methods=['GET'])
@auth_required
def get_class(id):
    class_ = Class.query.get_or_404(id)
    
    # Kiểm tra và cập nhật trạng thái nếu cần
    updated = update_class_status(class_)
    if updated:
        db.session.commit()
        
    return jsonify({
        "id": class_.id,
        "code": class_.code,
        "max_student": class_.max_student,
        "start_date": format_date(class_.start_date),
        "end_date": format_date(class_.end_date),
        "subject_id": class_.subject_id,
        "is_del": class_.is_del
    })

@class_bp.route('/classes/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_class(id):
    data = request.get_json()
    class_ = Class.query.get_or_404(id)
    
    start_date = class_.start_date
    end_date = class_.end_date
    
    if 'code' in data:
        class_.code = data['code']
    if 'max_student' in data:
        class_.max_student = data['max_student']
    if 'start_date' in data:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        class_.start_date = start_date
    if 'end_date' in data:
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        class_.end_date = end_date
    if 'subject_id' in data:
        class_.subject_id = data['subject_id']
    if 'is_del' in data:
        class_.is_del = data['is_del']
    
    # Validate end_date is after start_date
    if end_date <= start_date:
        return jsonify({"error": "Ngày kết thúc phải sau ngày bắt đầu"}), 400
    
    # Kiểm tra ngày kết thúc so với ngày hiện tại
    class_.is_del = end_date < date.today()
    
    db.session.commit()
    return jsonify({"message": "Class updated successfully"})

@class_bp.route('/classes/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_class(id):
    class_ = Class.query.get_or_404(id)
    db.session.delete(class_)
    db.session.commit()
    return jsonify({"message": "Class deleted successfully"})