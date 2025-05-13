from flask import Blueprint, request, jsonify, g
from app import db
from app.models.account import Account
from app.models.student import Student
from app.models.teacher import Teacher
from app.utils.auth import auth_required, admin_required, role_or_self_required
import jwt
import os

account_bp = Blueprint('account', __name__)

@account_bp.route('/accounts', methods=['POST'])
@admin_required
def create_account():
    data = request.get_json()
    new_account = Account(
        username=data['username'],
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        role=data['role'],
        student_id=data.get('student_id'),
        teacher_id=data.get('teacher_id'),
        is_active=data.get('is_active', True)
    )
    new_account.set_password(data['password'])  # Mã hóa mật khẩu trước khi lưu
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account created successfully"}), 201

@account_bp.route('/accounts/login', methods=['POST'])
def login_account():
    data = request.get_json()

    # Tìm tài khoản theo username, email hoặc số điện thoại
    account = Account.query.filter(
        (Account.username == data['identifier']) |
        (Account.email == data['identifier']) |
        (Account.phone_number == data['identifier'])
    ).first()

    if not account:
        return jsonify({"message": "Tài khoản không tồn tại"}), 404

    # Kiểm tra tài khoản & mật khẩu
    if account and account.check_password(data['password']):
        # Generate JWT token
        secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
        token_data = {
            'user_id': account.id,
            'role': account.role
            # Không thêm thời gian hết hạn (exp) để token tồn tại cho đến khi đăng xuất
        }
        
        # Thêm student_id/teacher_id vào token data nếu có
        if account.student_id:
            token_data['student_id'] = account.student_id
        if account.teacher_id:
            token_data['teacher_id'] = account.teacher_id
            
        token = jwt.encode(token_data, secret_key, algorithm="HS256")
        
        return jsonify({
            "token": token,
            "role": account.role,
            "username": account.username,
            "isActive": account.is_active,
            "student_id": account.student_id,
            "teacher_id": account.teacher_id
        }), 200
    else:
        return jsonify({"message": "Mật khẩu không chính xác"}), 401

@account_bp.route('/accounts', methods=['GET'])
@admin_required
def get_accounts():
    accounts = Account.query.all()
    return jsonify([{
        "id": account.id,
        "username": account.username,
        "email": account.email,
        "phone_number": account.phone_number,
        "role": account.role,
        "student_id": account.student_id,
        "teacher_id": account.teacher_id,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "updated_at": account.updated_at
    } for account in accounts])

@account_bp.route('/accounts/<int:id>', methods=['GET'])
@admin_required
def get_account(id):
    account = Account.query.get_or_404(id)
    return jsonify({
        "id": account.id,
        "username": account.username,
        "email": account.email,
        "phone_number": account.phone_number,
        "role": account.role,
        "student_id": account.student_id,
        "teacher_id": account.teacher_id,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "updated_at": account.updated_at
    })

@account_bp.route('/accounts/<int:id>', methods=['PUT'])
@admin_required
def update_account(id):
    data = request.get_json()
    account = Account.query.get_or_404(id)
    
    if 'username' in data:
        account.username = data['username']
    if 'email' in data:
        account.email = data['email']
    if 'phone_number' in data:
        account.phone_number = data['phone_number']
    if 'password' in data:
        account.set_password(data['password'])  # Mã hóa mật khẩu trước khi lưu
    if 'role' in data:
        account.role = data['role']
    if 'student_id' in data:
        account.student_id = data['student_id']
    if 'teacher_id' in data:
        account.teacher_id = data['teacher_id']
    if 'is_active' in data:
        account.is_active = data['is_active']
    
    db.session.commit()
    return jsonify({"message": "Account updated successfully"})

@account_bp.route('/accounts/<int:id>', methods=['DELETE'])
@admin_required
def delete_account(id):
    account = Account.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account deleted successfully"})

@account_bp.route('/profile', methods=['OPTIONS'])
def handle_profile_options():
    resp = jsonify({'success': True})
    # Thêm CORS headers
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Methods'] = 'GET, PUT, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Max-Age'] = '3600'
    return resp, 200

# New endpoint for getting user profile based on role
@account_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """
    Get profile information of currently logged in user.
    Returns student or teacher information based on the user's role.
    """
    if g.role == 'student' and g.student_id:
        # Get student profile
        student = Student.query.get_or_404(g.student_id)
        return jsonify({
            "id": student.id,
            "identity_number": student.identity_number,
            "email": student.email,
            "phone_number": student.phone_number,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "birthday": student.birthday.strftime('%d/%m/%Y') if student.birthday else None,
            "address": student.address,
            "avatar_url": student.avatar_url,
            "gender": student.gender,
            "face_encoding": student.face_encoding is not None
        })
    elif g.role == 'teacher' and g.teacher_id:
        # Get teacher profile
        teacher = Teacher.query.get_or_404(g.teacher_id)
        return jsonify({
            "id": teacher.id,
            "identity_number": teacher.identity_number,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name,
            "birthday": teacher.birthday.strftime('%d/%m/%Y') if teacher.birthday else None,
            "address": teacher.address,
            "gender": teacher.gender,
            "avatar_url": teacher.avatar_url,
            "bio": teacher.bio,
            "face_encoding": teacher.face_encoding is not None
        })
    elif g.role == 'admin':
        # For admin users, return basic info
        account = Account.query.filter_by(id=g.user_id).first()
        return jsonify({
            "username": account.username if account else None,
            "role": "admin",
            "message": "Admin users should use specific endpoints to manage profiles"
        })
    else:
        return jsonify({"message": "Không tìm thấy thông tin người dùng"}), 404

# Endpoint for updating user profile based on role
@account_bp.route('/profile', methods=['PUT'])
@auth_required
def update_profile():
    """
    Update profile information of currently logged in user.
    Updates student or teacher information based on the user's role.
    """
    data = request.get_json()
    
    if g.role == 'student' and g.student_id:
        # Update student profile
        student = Student.query.get_or_404(g.student_id)
          # Only allow updating certain fields
        if 'email' in data:
            student.email = data['email']
        if 'phone_number' in data:
            student.phone_number = data['phone_number']
        if 'address' in data:
            student.address = data['address']
        
        db.session.commit()
        return jsonify({"message": "Hồ sơ sinh viên đã được cập nhật thành công"})
        
    elif g.role == 'teacher' and g.teacher_id:
        # Update teacher profile
        teacher = Teacher.query.get_or_404(g.teacher_id)
          # Only allow updating certain fields
        if 'email' in data:
            teacher.email = data['email']
        if 'phone_number' in data:
            teacher.phone_number = data['phone_number']
        if 'address' in data:
            teacher.address = data['address']
        if 'bio' in data:
            teacher.bio = data['bio']
        
        db.session.commit()
        return jsonify({"message": "Hồ sơ giảng viên đã được cập nhật thành công"})
        
    else:
        return jsonify({"message": "Không tìm thấy thông tin người dùng để cập nhật"}), 404

@account_bp.route('/change-password', methods=['PUT'])
@auth_required
def change_password():
    """
    Change user password.
    Required fields in request body:
    - old_password: current password
    - new_password: new password
    """
    data = request.get_json()
    
    if 'old_password' not in data or 'new_password' not in data:
        return jsonify({"message": "Mật khẩu cũ và mật khẩu mới không được để trống"}), 400
        
    # Get the account from database
    account = Account.query.get_or_404(g.user_id)
    
    # Verify the old password
    if not account.check_password(data['old_password']):
        return jsonify({"message": "Mật khẩu cũ không chính xác"}), 401
    
    # Set the new password
    account.set_password(data['new_password'])
    
    db.session.commit()
    return jsonify({"message": "Mật khẩu đã được thay đổi thành công"})