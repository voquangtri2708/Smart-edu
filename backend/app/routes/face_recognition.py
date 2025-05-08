from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.models.teacher import Teacher
from app.ml.faces import encode_face, check_face, encode_face_from_base64
import logging

face_recognition_bp = Blueprint('face_recognition', __name__)

@face_recognition_bp.route('/recognize-face', methods=['POST'])
def recognize_face():
    """
    API nhận diện khuôn mặt từ ảnh đầu vào
    Input: {
        "image": "base64_encoded_string",      # Hình ảnh dưới dạng base64
        "role": "student" hoặc "teacher"       # Vai trò để tìm kiếm (không bắt buộc)
        "expected_id": "id của người dùng"     # ID mong đợi của người dùng (không bắt buộc)
    }
    Output:
    - Nếu nhận diện thành công: 
        {
            "recognized": true,
            "user": {thông tin người dùng},
            "matched_expected": true/false     # Có khớp với ID mong đợi không
        }
    - Nếu không nhận diện được: 
        {
            "recognized": false
        }
    """
    # Kiểm tra dữ liệu đầu vào
    if 'image' not in request.json:
        return jsonify({"message": "Thiếu dữ liệu ảnh"}), 400
    
    # Lấy dữ liệu ảnh (base64 encoded)
    image_data = request.json.get('image')
    role = request.json.get('role')  # Nếu có
    expected_id = request.json.get('expected_id')  # ID mong đợi nếu có
    
    # Log để debug
    logging.info(f"Face Recognition request: role={role}, expected_id={expected_id}")
    
    # Tạo face encoding trực tiếp từ ảnh base64
    face_embedding = encode_face_from_base64(image_data)
    
    if not face_embedding:
        return jsonify({
            "recognized": False,
            "message": "Không phát hiện khuôn mặt trong ảnh"
        }), 400
    
    # Tìm kiếm đối tượng phù hợp trong database
    match_found = False
    matched_user = None
    matched_expected = False
    
    # Chuyển expected_id thành string để so sánh chính xác, loại bỏ khoảng trắng
    if expected_id is not None:
        expected_id = str(expected_id).strip()
    
    # Tìm kiếm trong student nếu không chỉ định role hoặc role là student
    if not role or role == 'student':
        students = Student.query.filter(Student.face_encoding != None).all()
        for student in students:
            if check_face(face_embedding, student.face_encoding):
                match_found = True
                
                # Chuyển ID của student thành string để so sánh
                student_id_str = str(student.id).strip()
                
                matched_user = {
                    "id": student.id,
                    "role": "student",
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email,
                    "avatar_url": student.avatar_url
                }
                
                # Log để debug
                logging.info(f"Found matching student: id={student_id_str}, expected_id={expected_id}")
                
                # Kiểm tra nếu ID được nhận diện khớp với ID mong đợi
                if expected_id and student_id_str == expected_id:
                    matched_expected = True
                    logging.info("IDs match!")
                else:
                    logging.info(f"IDs don't match. Student ID={student_id_str}, Expected ID={expected_id}")
                
                break
    
    # Tìm kiếm trong teacher nếu không tìm thấy trong student hoặc role là teacher
    if (not match_found and not role) or role == 'teacher':
        teachers = Teacher.query.filter(Teacher.face_encoding != None).all()
        for teacher in teachers:
            if check_face(face_embedding, teacher.face_encoding):
                match_found = True
                
                # Chuyển ID của teacher thành string để so sánh
                teacher_id_str = str(teacher.id).strip()
                
                matched_user = {
                    "id": teacher.id,
                    "role": "teacher",
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "email": teacher.email,
                    "avatar_url": teacher.avatar_url
                }
                
                # Log để debug
                logging.info(f"Found matching teacher: id={teacher_id_str}, expected_id={expected_id}")
                
                # Kiểm tra nếu ID được nhận diện khớp với ID mong đợi
                if expected_id and teacher_id_str == expected_id:
                    matched_expected = True
                    logging.info("IDs match!")
                else:
                    logging.info(f"IDs don't match. Teacher ID={teacher_id_str}, Expected ID={expected_id}")
                
                break
    
    # Log kết quả cuối cùng
    logging.info(f"Final result: recognized={match_found}, matched_expected={matched_expected}")
    
    if match_found:
        return jsonify({
            "recognized": True,
            "user": matched_user,
            "matched_expected": matched_expected
        })
    else:
        return jsonify({
            "recognized": False,
            "message": "Không tìm thấy khuôn mặt phù hợp trong hệ thống"
        })

@face_recognition_bp.route('/retrain-face/<string:role>/<string:user_id>', methods=['POST'])
def retrain_face(role, user_id):
    """
    API để huấn luyện lại khuôn mặt cho một người dùng cụ thể
    Input:
        - role: "student" hoặc "teacher"
        - user_id: ID của người dùng
    Output:
        - Thông báo thành công hoặc thất bại
    """
    if role == 'student':
        user = Student.query.get_or_404(user_id)
    elif role == 'teacher':
        user = Teacher.query.get_or_404(user_id)
    else:
        return jsonify({"message": "Vai trò không hợp lệ. Hãy chọn 'student' hoặc 'teacher'"}), 400
    
    if not user.avatar_url:
        return jsonify({"message": "Người dùng chưa có ảnh avatar"}), 400
    
    # Tạo face encoding từ ảnh avatar
    face_encoding = encode_face(user.avatar_url)
    
    if not face_encoding:
        return jsonify({
            "success": False,
            "message": "Không phát hiện khuôn mặt trong ảnh avatar"
        }), 400
    
    # Cập nhật face encoding trong database
    user.face_encoding = face_encoding
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Đã huấn luyện lại nhận diện khuôn mặt thành công"
    }) 