from flask import Blueprint, request, jsonify, g
from app import db
from app.models.building import Building
from app.models.campus import Campus  # Import Campus model for validation
from app.utils.auth import auth_required, admin_required

building_bp = Blueprint('building', __name__)

@building_bp.route('/buildings', methods=['POST'])
@auth_required
@admin_required
def create_building():
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['name', 'campus_id']):
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400
    
    try:
        # Validate campus_id exists
        campus = Campus.query.get(data['campus_id'])
        if not campus:
            return jsonify({"error": f"Campus ID {data['campus_id']} không tồn tại"}), 400
            
        new_building = Building(
            name=data['name'],
            campus_id=data['campus_id']
        )
        db.session.add(new_building)
        db.session.commit()
        return jsonify({"message": "Building created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@building_bp.route('/buildings', methods=['GET'])
@auth_required
def get_buildings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('query', '')
        campus_id = request.args.get('campus_id')

        # Limit per_page to prevent performance issues
        if per_page > 100:
            per_page = 100
        
        # Filter buildings based on search query
        query = Building.query
        if search_query:
            query = query.filter(Building.name.ilike(f'%{search_query}%'))
        
        # Filter by campus_id if provided
        if campus_id:
            # Convert campus_id to integer safely
            try:
                campus_id_int = int(campus_id)
                
                # Check if campus exists
                campus = Campus.query.get(campus_id_int)
                if not campus:
                    return jsonify({"error": f"Campus ID {campus_id} không tồn tại"}), 404
                    
                query = query.filter(Building.campus_id == campus_id_int)
            except ValueError:
                return jsonify({"error": f"Campus ID phải là số nguyên: {campus_id}"}), 400
        
        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        buildings = pagination.items
        
        return jsonify({
            'items': [{
                "id": building.id,
                "name": building.name,
                "campus_id": building.campus_id
            } for building in buildings],
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@building_bp.route('/buildings/<int:id>', methods=['GET'])
@auth_required
def get_building(id):
    try:
        building = Building.query.get_or_404(id)
        return jsonify({
            "id": building.id,
            "name": building.name,
            "campus_id": building.campus_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@building_bp.route('/buildings/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_building(id):
    data = request.get_json()
    
    try:
        building = Building.query.get_or_404(id)
        
        if 'name' in data:
            building.name = data['name']
        if 'campus_id' in data:
            # Validate campus_id exists
            campus = Campus.query.get(data['campus_id'])
            if not campus:
                return jsonify({"error": f"Campus ID {data['campus_id']} không tồn tại"}), 400
                
            building.campus_id = data['campus_id']
        
        db.session.commit()
        return jsonify({"message": "Building updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@building_bp.route('/buildings/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_building(id):
    try:
        building = Building.query.get_or_404(id)
        db.session.delete(building)
        db.session.commit()
        return jsonify({"message": "Building deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500