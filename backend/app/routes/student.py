from flask import Blueprint, request, jsonify, g
from app import db
from app.models.student import Student
from app.utils.auth import auth_required, admin_required, student_self_or_admin_required
from datetime import datetime
from app.ml.faces import encode_face

student_bp = Blueprint('student', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@student_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    face_encoding = None
    
    if avatar_url:
        face_encoding = encode_face(avatar_url)
    
    new_student = Student(
        id=data['id'],
        identity_number=data['identity_number'],
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        first_name=data['first_name'],
        last_name=data['last_name'],
        birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
        address=data['address'],
        avatar_url=avatar_url,
        gender=data.get('gender', 'MALE'),
        face_encoding=face_encoding
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student created successfully"}), 201

@student_bp.route('/students', methods=['GET'])
@auth_required
@admin_required
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Filter students based on search query
    query = Student.query
    if search_query:
        query = query.filter(
            # Search by ID or name
            (Student.id.ilike(f'%{search_query}%')) |
            (Student.first_name.ilike(f'%{search_query}%')) |
            (Student.last_name.ilike(f'%{search_query}%')) |
            (Student.identity_number.ilike(f'%{search_query}%'))
        )
    
    # Apply pagination to the filtered query
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
            'address': student.address,
            'avatar_url': student.avatar_url,
            'gender': student.gender,
            'face_encoding': student.face_encoding is not None
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

@student_bp.route('/students/<string:id>', methods=['GET'])
@student_self_or_admin_required
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        "id": student.id,
        "identity_number": student.identity_number,
        "email": student.email,
        "phone_number": student.phone_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "birthday": format_date(student.birthday),
        "address": student.address,
        "avatar_url": student.avatar_url,
        "gender": student.gender,
        "face_encoding": student.face_encoding is not None
    })

@student_bp.route('/students/<string:id>', methods=['PUT'])
@student_self_or_admin_required
def update_student(id):
    data = request.get_json()
    student = Student.query.get_or_404(id)
    
    if 'identity_number' in data:
        student.identity_number = data['identity_number']
    if 'email' in data:
        student.email = data['email']
    if 'phone_number' in data:
        student.phone_number = data['phone_number']
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'birthday' in data:
        student.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
    if 'address' in data:
        student.address = data['address']
    if 'gender' in data:
        student.gender = data['gender']
    if 'avatar_url' in data:
        student.avatar_url = data['avatar_url']
        # Update face encoding when avatar URL is updated
        if student.avatar_url:
            student.face_encoding = encode_face(student.avatar_url)
    
    db.session.commit()
    return jsonify({"message": "Student updated successfully"})

@student_bp.route('/students/<string:id>', methods=['DELETE'])
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"})