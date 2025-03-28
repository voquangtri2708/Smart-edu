from flask import Blueprint, request, jsonify, g
from app import db
from app.models.student import Student
from datetime import datetime
from app.routes.account import admin_required, role_or_self_required, auth_required
from werkzeug.security import generate_password_hash

student_bp = Blueprint('student', __name__)

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@student_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json()
    
    # Kiểm tra gender đã được thêm vào database chưa
    try:
        new_student = Student(
            id=data['id'],
            identity_number=data['identity_number'],
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
            address=data['address'],
            gender=data.get('gender', 'MALE')  # Giá trị mặc định là MALE
        )
    except Exception as e:
        # Nếu có lỗi (ví dụ như gender chưa được thêm vào model), thử cách khác
        new_student = Student(
            id=data['id'],
            identity_number=data['identity_number'],
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date(),
            address=data['address']
        )
    
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student created successfully"}), 201

@student_bp.route('/students', methods=['GET'])
@admin_required
def get_students():
    students = Student.query.all()
    result = []
    
    for student in students:
        student_data = {
            "id": student.id,
            "identity_number": student.identity_number,
            "email": student.email,
            "phone_number": student.phone_number,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "birthday": format_date(student.birthday),
            "address": student.address
        }
        
        # Thêm gender nếu tồn tại trong model
        try:
            student_data["gender"] = student.gender
        except:
            pass
            
        result.append(student_data)
        
    return jsonify(result)

@student_bp.route('/students/<string:id>', methods=['GET'])
@role_or_self_required
def get_student(id):
    student = Student.query.get_or_404(id)
    student_data = {
        "id": student.id,
        "identity_number": student.identity_number,
        "email": student.email,
        "phone_number": student.phone_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "birthday": format_date(student.birthday),
        "address": student.address
    }
    
    # Thêm gender nếu tồn tại trong model
    try:
        student_data["gender"] = student.gender
    except:
        pass
        
    return jsonify(student_data)

@student_bp.route('/students/<string:id>', methods=['PUT'])
@role_or_self_required
def update_student(id):
    data = request.get_json()
    student = Student.query.get_or_404(id)
    
    # Chỉ admin được phép cập nhật tất cả các trường
    if g.role == 'admin':
        if 'identity_number' in data:
            student.identity_number = data['identity_number']
        if 'id' in data:
            student.id = data['id']
        if 'first_name' in data:
            student.first_name = data['first_name']
        if 'last_name' in data:
            student.last_name = data['last_name']
        if 'birthday' in data:
            student.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        if 'address' in data:
            student.address = data['address']
        # Cập nhật gender nếu có trong model và trong dữ liệu đầu vào
        try:
            if 'gender' in data:
                student.gender = data['gender']
        except:
            pass
    
    # Các trường có thể cập nhật bởi cả admin và student (người dùng thường)
    if 'email' in data:
        student.email = data['email']
    if 'phone_number' in data:
        student.phone_number = data['phone_number']
    if 'password' in data and data['password']:
        student.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({"message": "Student updated successfully"})

@student_bp.route('/students/<string:id>', methods=['DELETE'])
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"})

@student_bp.route('/profile', methods=['GET'])
@auth_required
def get_own_profile():
    # Kiểm tra xem người dùng có phải là sinh viên không
    if g.role != 'student' or not g.student_id:
        return jsonify({"message": "Bạn không phải là sinh viên"}), 403
        
    student = Student.query.get_or_404(g.student_id)
    student_data = {
        "id": student.id,
        "identity_number": student.identity_number,
        "email": student.email,
        "phone_number": student.phone_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "birthday": format_date(student.birthday),
        "address": student.address
    }
    
    # Thêm gender nếu tồn tại trong model
    try:
        student_data["gender"] = student.gender
    except:
        pass
        
    return jsonify(student_data)