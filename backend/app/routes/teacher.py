from flask import Blueprint, request, jsonify, g
from app import db
from app.models.teacher import Teacher
from app.utils.auth import auth_required, admin_required, teacher_self_or_admin_required
from datetime import datetime
from app.ml.faces import encode_face

teacher_bp = Blueprint('teacher', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@teacher_bp.route('/teachers', methods=['POST'])
@admin_required
def create_teacher():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    face_encoding = None
    
    if avatar_url:
        face_encoding = encode_face(avatar_url)
    
    new_teacher = Teacher(
        id=data['id'],
        identity_number=data['identity_number'],
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        first_name=data['first_name'],
        last_name=data['last_name'],
        birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
        address=data['address'],
        gender=data.get('gender'),
        avatar_url=avatar_url,
        bio=data.get('bio'),
        face_encoding=face_encoding
    )
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify({"message": "Teacher created successfully"}), 201

@teacher_bp.route('/teachers', methods=['GET'])
@admin_required
def get_teachers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('query', '')
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Filter teachers based on search query
    query = Teacher.query
    if search_query:
        query = query.filter(
            # Search by ID or name
            (Teacher.id.ilike(f'%{search_query}%')) |
            (Teacher.first_name.ilike(f'%{search_query}%')) |
            (Teacher.last_name.ilike(f'%{search_query}%')) |
            (Teacher.identity_number.ilike(f'%{search_query}%'))
        )
    
    # Apply pagination to the filtered query
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    teachers = pagination.items
    
    return jsonify({
        'items': [{
            "id": teacher.id,
            "identity_number": teacher.identity_number,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name,
            "birthday": format_date(teacher.birthday),
            "address": teacher.address,
            "gender": teacher.gender,
            "avatar_url": teacher.avatar_url,
            "bio": teacher.bio,
            "face_encoding": teacher.face_encoding is not None
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

@teacher_bp.route('/teachers/<string:id>', methods=['GET'])
@teacher_self_or_admin_required
def get_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    return jsonify({
        "id": teacher.id,
        "identity_number": teacher.identity_number,
        "email": teacher.email,
        "phone_number": teacher.phone_number,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "birthday": format_date(teacher.birthday),
        "address": teacher.address,
        "gender": teacher.gender,
        "avatar_url": teacher.avatar_url,
        "bio": teacher.bio,
        "face_encoding": teacher.face_encoding is not None
    })

@teacher_bp.route('/teachers/<string:id>', methods=['PUT'])
@teacher_self_or_admin_required
def update_teacher(id):
    data = request.get_json()
    teacher = Teacher.query.get_or_404(id)
    
    if 'identity_number' in data:
        teacher.identity_number = data['identity_number']
    if 'email' in data:
        teacher.email = data['email']
    if 'phone_number' in data:
        teacher.phone_number = data['phone_number']
    if 'first_name' in data:
        teacher.first_name = data['first_name']
    if 'last_name' in data:
        teacher.last_name = data['last_name']
    if 'birthday' in data:
        teacher.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
    if 'address' in data:
        teacher.address = data['address']
    if 'gender' in data:
        teacher.gender = data['gender']
    if 'avatar_url' in data:
        teacher.avatar_url = data['avatar_url']
        # Update face encoding when avatar URL is updated
        if teacher.avatar_url:
            teacher.face_encoding = encode_face(teacher.avatar_url)
    if 'bio' in data:
        teacher.bio = data['bio']
    
    db.session.commit()
    return jsonify({"message": "Teacher updated successfully"})

@teacher_bp.route('/teachers/<string:id>', methods=['DELETE'])
@admin_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted successfully"})