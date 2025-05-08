from flask import Blueprint, request, jsonify, g
from app import db
from app.models.student import Student
from app.models.teacher import Teacher
from app.utils.cloudinary_helper import upload_image
from app.utils.auth import auth_required, admin_required
from app.ml.faces import encode_face

avatar_bp = Blueprint('avatar', __name__)

@avatar_bp.route('/upload-avatar', methods=['POST'])
@auth_required
@admin_required  # Chỉ admin mới được phép upload avatar
def upload_avatar():
    """
    Upload avatar cho student hoặc teacher
    Yêu cầu: Người dùng phải có quyền admin
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
    
    return jsonify({"message": "Thiếu thông tin student_id hoặc teacher_id"}), 400