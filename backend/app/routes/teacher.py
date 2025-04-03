from flask import Blueprint, request, jsonify
from app import db
from app.models.teacher import Teacher
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@teacher_bp.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.get_json()
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
        avatar_url=data.get('avatar_url'),
        bio=data.get('bio')
    )
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify({"message": "Teacher created successfully"}), 201

@teacher_bp.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([{
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
        "bio": teacher.bio
    } for teacher in teachers])

@teacher_bp.route('/teachers/<string:id>', methods=['GET'])
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
        "bio": teacher.bio
    })

@teacher_bp.route('/teachers/<string:id>', methods=['PUT'])
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
    if 'bio' in data:
        teacher.bio = data['bio']
    
    db.session.commit()
    return jsonify({"message": "Teacher updated successfully"})

@teacher_bp.route('/teachers/<string:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted successfully"})