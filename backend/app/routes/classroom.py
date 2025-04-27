from flask import Blueprint, request, jsonify
from app import db
from app.models.classroom import Classroom
from app.models.building import Building  # Import Building model for validation
from app.utils.auth import auth_required, admin_required
import logging  # Add logging

classroom_bp = Blueprint('classroom', __name__)

@classroom_bp.route('/classrooms', methods=['POST'])
@auth_required
@admin_required
def create_classroom():
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['room_number', 'capacity', 'building_id']):
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400
    
    try:
        # Validate building_id exists
        building = Building.query.get(data['building_id'])
        if not building:
            return jsonify({"error": f"Building ID {data['building_id']} không tồn tại"}), 400
            
        new_classroom = Classroom(
            room_number=data['room_number'],
            capacity=data['capacity'],
            building_id=data['building_id'],
            facilities=data.get('facilities')
        )
        db.session.add(new_classroom)
        db.session.commit()
        return jsonify({"message": "Classroom created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating classroom: {str(e)}")
        return jsonify({"error": str(e)}), 500

@classroom_bp.route('/classrooms', methods=['GET'])
@auth_required
def get_classrooms():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('query', '')
        building_id = request.args.get('building_id')
        
        # Log the parameters received
        logging.info(f"GET /classrooms with params: page={page}, per_page={per_page}, query={search_query}, building_id={building_id}")
        
        # Limit per_page to prevent performance issues
        if per_page > 100:
            per_page = 100
        
        # Filter classrooms based on search query
        query = Classroom.query
        if search_query:
            query = query.filter(Classroom.room_number.ilike(f'%{search_query}%'))
        
        # Filter by building_id if provided
        if building_id:
            # Convert building_id to integer safely
            try:
                building_id_int = int(building_id)
                
                # Check if building exists
                building = Building.query.get(building_id_int)
                if not building:
                    return jsonify({"error": f"Building ID {building_id} không tồn tại"}), 404
                    
                query = query.filter(Classroom.building_id == building_id_int)
            except ValueError:
                return jsonify({"error": f"Building ID phải là số nguyên: {building_id}"}), 400
        
        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        classrooms = pagination.items
        
        return jsonify({
            'items': [{
                "id": classroom.id,
                "room_number": classroom.room_number,
                "capacity": classroom.capacity,
                "building_id": classroom.building_id,
                "facilities": classroom.facilities
            } for classroom in classrooms],
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
        logging.error(f"Error getting classrooms: {str(e)}")
        return jsonify({"error": str(e)}), 500

@classroom_bp.route('/classrooms/<int:id>', methods=['GET'])
@auth_required
def get_classroom(id):
    try:
        classroom = Classroom.query.get_or_404(id)
        return jsonify({
            "id": classroom.id,
            "room_number": classroom.room_number,
            "capacity": classroom.capacity,
            "building_id": classroom.building_id,
            "facilities": classroom.facilities
        })
    except Exception as e:
        logging.error(f"Error getting classroom {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@classroom_bp.route('/classrooms/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_classroom(id):
    data = request.get_json()
    
    try:
        classroom = Classroom.query.get_or_404(id)
        
        if 'room_number' in data:
            classroom.room_number = data['room_number']
        if 'capacity' in data:
            classroom.capacity = data['capacity']
        if 'building_id' in data:
            # Validate building_id exists
            building = Building.query.get(data['building_id'])
            if not building:
                return jsonify({"error": f"Building ID {data['building_id']} không tồn tại"}), 400
                
            classroom.building_id = data['building_id']
        if 'facilities' in data:
            classroom.facilities = data['facilities']
        
        db.session.commit()
        return jsonify({"message": "Classroom updated successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating classroom {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@classroom_bp.route('/classrooms/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_classroom(id):
    try:
        classroom = Classroom.query.get_or_404(id)
        db.session.delete(classroom)
        db.session.commit()
        return jsonify({"message": "Classroom deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting classroom {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500