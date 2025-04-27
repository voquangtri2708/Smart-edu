from flask import Blueprint, request, jsonify
from app import db
from app.models.campus import Campus
from app.utils.auth import auth_required, admin_required

campus_bp = Blueprint('campus', __name__)

@campus_bp.route('/campuses', methods=['POST'])
@auth_required
@admin_required
def create_campus():
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['name', 'address']):
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400
    
    try:
        new_campus = Campus(
            name=data['name'],
            address=data['address']
        )
        db.session.add(new_campus)
        db.session.commit()
        return jsonify({"message": "Campus created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@campus_bp.route('/campuses', methods=['GET'])
@auth_required
def get_campuses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Filter campuses based on search query
    query = Campus.query
    if search_query:
        query = query.filter(
            (Campus.name.ilike(f'%{search_query}%')) | 
            (Campus.address.ilike(f'%{search_query}%'))
        )
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    campuses = pagination.items
    
    return jsonify({
        'items': [{
            "id": campus.id,
            "name": campus.name,
            "address": campus.address
        } for campus in campuses],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@campus_bp.route('/campuses/<int:id>', methods=['GET'])
@auth_required
def get_campus(id):
    campus = Campus.query.get_or_404(id)
    return jsonify({
        "id": campus.id,
        "name": campus.name,
        "address": campus.address
    })

@campus_bp.route('/campuses/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_campus(id):
    data = request.get_json()
    campus = Campus.query.get_or_404(id)
    
    try:
        if 'name' in data:
            campus.name = data['name']
        if 'address' in data:
            campus.address = data['address']
        
        db.session.commit()
        return jsonify({"message": "Campus updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@campus_bp.route('/campuses/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_campus(id):
    try:
        campus = Campus.query.get_or_404(id)
        db.session.delete(campus)
        db.session.commit()
        return jsonify({"message": "Campus deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500