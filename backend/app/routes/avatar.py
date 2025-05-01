from flask import Blueprint, request, jsonify, g
from app import db
from app.models.student import Student
from app.models.teacher import Teacher
from app.utils.cloudinary_helper import upload_image
from app.routes.account import auth_required
from app.ml.faces import encode_face

avatar_bp = Blueprint('avatar', __name__)

@avatar_bp.route('/upload-avatar', methods=['POST'])
@auth_required
def upload_avatar():
    """
    Upload avatar cho student hoặc teacher
    Yêu cầu: Người dùng phải đăng nhập
    """
    # Kiểm tra dữ liệu đầu vào
    if 'image' not in request.json:
        return jsonify({"message": "Thiếu dữ liệu ảnh"}), 400
    
    # Lấy dữ liệu ảnh (base64 encoded)
    image_data = request.json.get('image')
    
    # Upload ảnh lên Cloudinary
    avatar_url = upload_image(image_data)
    
    if not avatar_url:
        return jsonify({"message": "Không thể tải ảnh lên. Vui lòng thử lại."}), 500
    
    # Tạo face encoding từ ảnh avatar
    face_encoding = encode_face(avatar_url)
    
    # Cho phép admin cập nhật avatar cho bất kỳ tài khoản nào
    if g.role == 'admin':
        # Kiểm tra xem có teacher_id hoặc student_id được chỉ định không
        teacher_id = request.json.get('teacher_id')
        student_id = request.json.get('student_id')
        
        if teacher_id:
            teacher = Teacher.query.get_or_404(teacher_id)
            teacher.avatar_url = avatar_url
            teacher.face_encoding = face_encoding
            db.session.commit()
            return jsonify({
                "message": "Avatar cập nhật thành công",
                "avatar_url": avatar_url,
                "face_detected": face_encoding is not None
            })
        elif student_id:
            student = Student.query.get_or_404(student_id)
            student.avatar_url = avatar_url
            student.face_encoding = face_encoding
            db.session.commit()
            return jsonify({
                "message": "Avatar cập nhật thành công",
                "avatar_url": avatar_url,
                "face_detected": face_encoding is not None
            })
        # Nếu admin không chỉ định ID cụ thể, kiểm tra xem admin đó có teacher_id hoặc student_id không
        elif g.teacher_id:
            teacher = Teacher.query.get(g.teacher_id)
            if teacher:
                teacher.avatar_url = avatar_url
                teacher.face_encoding = face_encoding
                db.session.commit()
                return jsonify({
                    "message": "Avatar cập nhật thành công",
                    "avatar_url": avatar_url,
                    "face_detected": face_encoding is not None
                })
        elif g.student_id:
            student = Student.query.get(g.student_id)
            if student:
                student.avatar_url = avatar_url
                student.face_encoding = face_encoding
                db.session.commit()
                return jsonify({
                    "message": "Avatar cập nhật thành công",
                    "avatar_url": avatar_url,
                    "face_detected": face_encoding is not None
                })
        
        return jsonify({"message": "Không tìm thấy thông tin người dùng để cập nhật avatar"}), 400
                
    # Cập nhật avatar_url trong database cho người dùng thông thường
    elif g.role == 'student':
        if g.student_id:
            student = Student.query.get(g.student_id)
            if student:
                student.avatar_url = avatar_url
                student.face_encoding = face_encoding
                db.session.commit()
                return jsonify({
                    "message": "Avatar cập nhật thành công",
                    "avatar_url": avatar_url,
                    "face_detected": face_encoding is not None
                })
        return jsonify({"message": "Không tìm thấy thông tin người dùng để cập nhật avatar"}), 400
    
    elif g.role == 'teacher':
        if g.teacher_id:
            teacher = Teacher.query.get(g.teacher_id)
            if teacher:
                teacher.avatar_url = avatar_url
                teacher.face_encoding = face_encoding
                db.session.commit()
                return jsonify({
                    "message": "Avatar cập nhật thành công",
                    "avatar_url": avatar_url,
                    "face_detected": face_encoding is not None
                })
        return jsonify({"message": "Không tìm thấy thông tin người dùng để cập nhật avatar"}), 400
    
    else:
        return jsonify({"message": "Bạn không có quyền cập nhật avatar"}), 403 