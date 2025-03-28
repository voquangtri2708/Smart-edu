from flask import Blueprint, request, jsonify, g
from app import db
from app.models.teacher import Teacher
from datetime import datetime
from app.routes.account import admin_required, role_or_self_required, auth_required
from werkzeug.security import generate_password_hash

teacher_bp = Blueprint('teacher', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@teacher_bp.route('/teachers', methods=['POST'])
@admin_required
def create_teacher():
    data = request.get_json()
    
    # Kiểm tra gender đã được thêm vào database chưa
    try:
        new_teacher = Teacher(
            id=data['id'],
            identity_number=data['identity_number'],
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
            address=data['address'],
            bio=data.get('bio'),
            gender=data.get('gender', 'MALE')  # Giá trị mặc định là MALE
        )
    except Exception as e:
        # Nếu có lỗi (ví dụ như gender chưa được thêm vào model), thử cách khác
        new_teacher = Teacher(
            id=data['id'],
            identity_number=data['identity_number'],
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
            address=data['address'],
            bio=data.get('bio')
        )
    
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify({"message": "Teacher created successfully"}), 201

@teacher_bp.route('/teachers', methods=['GET'])
@admin_required
def get_teachers():
    teachers = Teacher.query.all()
    result = []
    
    for teacher in teachers:
        teacher_data = {
            "id": teacher.id,
            "identity_number": teacher.identity_number,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name,
            "birthday": format_date(teacher.birthday),
            "address": teacher.address,
            "bio": teacher.bio,
            "avatar_url": teacher.avatar_url
        }
        
        # Thêm gender nếu tồn tại trong database
        try:
            teacher_data["gender"] = teacher.gender
        except:
            pass
            
        result.append(teacher_data)
        
    return jsonify(result)

@teacher_bp.route('/teachers/<string:id>', methods=['GET'])
@role_or_self_required
def get_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    teacher_data = {
        "id": teacher.id,
        "identity_number": teacher.identity_number,
        "email": teacher.email,
        "phone_number": teacher.phone_number,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "birthday": format_date(teacher.birthday),
        "address": teacher.address,
        "bio": teacher.bio,
        "avatar_url": teacher.avatar_url
    }
    
    # Thêm gender nếu tồn tại trong database
    try:
        teacher_data["gender"] = teacher.gender
    except:
        pass
        
    return jsonify(teacher_data)

@teacher_bp.route('/teachers/<string:id>', methods=['PUT'])
@role_or_self_required
def update_teacher(id):
    data = request.get_json()
    teacher = Teacher.query.get_or_404(id)
    
    # Chỉ admin được phép cập nhật tất cả các trường
    if g.role == 'admin':
        if 'identity_number' in data:
            teacher.identity_number = data['identity_number']
        if 'id' in data:
            teacher.id = data['id']
        if 'first_name' in data:
            teacher.first_name = data['first_name']
        if 'last_name' in data:
            teacher.last_name = data['last_name']
        if 'birthday' in data:
            teacher.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        if 'address' in data:
            teacher.address = data['address']
        if 'bio' in data:
            teacher.bio = data['bio']
        if 'avatar_url' in data:
            teacher.avatar_url = data['avatar_url']
        # Cập nhật gender nếu có trong model và trong dữ liệu đầu vào
        try:
            if 'gender' in data:
                teacher.gender = data['gender']
        except:
            pass
    
    # Các trường có thể cập nhật bởi cả admin và teacher (người dùng thường)
    if 'email' in data:
        teacher.email = data['email']
    if 'phone_number' in data:
        teacher.phone_number = data['phone_number']
    if 'password' in data and data['password']:
        teacher.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({"message": "Teacher updated successfully"})

@teacher_bp.route('/teachers/<string:id>', methods=['DELETE'])
@admin_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted successfully"})

@teacher_bp.route('/profile', methods=['GET'])
@auth_required
def get_own_profile():
    # Kiểm tra xem người dùng có phải là giảng viên không
    if g.role != 'teacher' or not g.teacher_id:
        return jsonify({"message": "Bạn không phải là giảng viên"}), 403
        
    teacher = Teacher.query.get_or_404(g.teacher_id)
    teacher_data = {
        "id": teacher.id,
        "identity_number": teacher.identity_number,
        "email": teacher.email,
        "phone_number": teacher.phone_number,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "birthday": format_date(teacher.birthday),
        "address": teacher.address,
        "bio": teacher.bio,
        "avatar_url": teacher.avatar_url
    }
    
    # Thêm gender nếu tồn tại trong database
    try:
        teacher_data["gender"] = teacher.gender
    except:
        pass
        
    return jsonify(teacher_data)