from flask import Blueprint, request, jsonify, g
from app import db
from app.models.classs import Class
from app.utils.auth import auth_required, admin_required
from datetime import datetime

class_bp = Blueprint('class', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

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
    
    new_class = Class(
        code=data['code'],
        max_student=data['max_student'],
        start_date=start_date,
        end_date=end_date,
        subject_id=data.get('subject_id')  # Changed to get with default None since it's nullable
    )
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": "Class created successfully"}), 201

@class_bp.route('/classes', methods=['GET'])
@auth_required
def get_classes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
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
            "subject_id": class_.subject_id
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
    return jsonify({
        "id": class_.id,
        "code": class_.code,
        "max_student": class_.max_student,
        "start_date": format_date(class_.start_date),
        "end_date": format_date(class_.end_date),
        "subject_id": class_.subject_id
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
    
    # Validate end_date is after start_date
    if end_date <= start_date:
        return jsonify({"error": "Ngày kết thúc phải sau ngày bắt đầu"}), 400
    
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