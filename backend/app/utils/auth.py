from functools import wraps
from flask import g, jsonify, request
import jwt
import os

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Không tìm thấy token xác thực"}), 401
        
        try:
            # Get the token (remove 'Bearer ' if present)
            token = auth_header.split("Bearer ")[1] if "Bearer " in auth_header else auth_header
            
            # Verify the token
            secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
            data = jwt.decode(token, secret_key, algorithms=["HS256"], options={"verify_exp": False})
                
            # Store user info for the route handler
            g.user_id = data.get('user_id')
            g.role = data.get('role')
            g.student_id = data.get('student_id')
            g.teacher_id = data.get('teacher_id')
            g.is_admin = data.get('role') == 'admin'
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token đã hết hạn"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token không hợp lệ"}), 401
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_required_result = auth_required(lambda *a, **kw: None)(*args, **kwargs)
        if isinstance(auth_required_result, tuple):
            return auth_required_result
            
        if g.role != 'admin':
            return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Add the missing teacher_or_admin_required decorator
def teacher_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_required_result = auth_required(lambda *a, **kw: None)(*args, **kwargs)
        if isinstance(auth_required_result, tuple):
            return auth_required_result
            
        # Allow admin and teacher roles
        if g.role in ['admin', 'teacher']:
            return f(*args, **kwargs)
            
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    return decorated_function

# Thêm decorator mới cho student hoặc admin
def student_self_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_required_result = auth_required(lambda *a, **kw: None)(*args, **kwargs)
        if isinstance(auth_required_result, tuple):
            return auth_required_result
        
        # Get student ID from URL parameter
        student_id = kwargs.get('id')
        
        # Allow admin to access all student records
        if g.role == 'admin':
            return f(*args, **kwargs)
            
        # Allow students to access their own records
        if g.student_id == student_id:
            return f(*args, **kwargs)
            
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    return decorated_function

# Thêm decorator mới cho teacher hoặc admin
def teacher_self_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_required_result = auth_required(lambda *a, **kw: None)(*args, **kwargs)
        if isinstance(auth_required_result, tuple):
            return auth_required_result
        
        # Get teacher ID from URL parameter
        teacher_id = kwargs.get('id')
        
        # Allow admin to access all teacher records
        if g.role == 'admin':
            return f(*args, **kwargs)
            
        # Allow teachers to access their own records
        if g.teacher_id == teacher_id:
            return f(*args, **kwargs)
            
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    return decorated_function

# Decorator linh hoạt để kiểm tra quyền admin hoặc người dùng sửa thông tin chính mình
def role_or_self_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_required_result = auth_required(lambda *a, **kw: None)(*args, **kwargs)
        if isinstance(auth_required_result, tuple):
            return auth_required_result
            
        # Cho phép admin thao tác mọi tài khoản
        if g.role == 'admin':
            return f(*args, **kwargs)
            
        # Lấy tài khoản từ ID resource
        resource_id = kwargs.get('id')
        
        # Kiểm tra xem người này có đang truy cập profile của chính mình không
        if (g.role == 'student' and g.student_id == resource_id) or \
           (g.role == 'teacher' and g.teacher_id == resource_id):
            return f(*args, **kwargs)
            
        return jsonify({"message": "Bạn không có quyền thực hiện hành động này"}), 403
    return decorated_function
