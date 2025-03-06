from flask import Blueprint, request, jsonify
from app import db
from app.models.account import Account
from datetime import datetime

account_bp = Blueprint('account', __name__)

@account_bp.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    new_account = Account(
        username=data['username'],
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        password=data['password'],  # Lưu ý: cần hash mật khẩu trước khi lưu
        role=data['role'],
        student_id=data.get('student_id'),
        teacher_id=data.get('teacher_id'),
        is_active=data.get('is_active', True)
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account created successfully"}), 201

@account_bp.route('/accounts', methods=['GET'])
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
        account.password = data['password']  # Lưu ý: cần hash mật khẩu trước khi lưu
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
def delete_account(id):
    account = Account.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account deleted successfully"})