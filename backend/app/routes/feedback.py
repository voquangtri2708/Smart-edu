from flask import Blueprint, request, jsonify, g
from app import db
from app.models.feedback import Feedback
from app.models.classs import Class
from app.models.class_student import ClassStudent
from app.models.class_teacher import ClassTeacher
from app.ml.pred import prediction
from app.utils.auth import auth_required, admin_required, student_self_or_admin_required
from datetime import datetime
from sqlalchemy.exc import IntegrityError

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedbacks', methods=['POST'])
@auth_required
def create_feedback():
    data = request.get_json()
    
    # Chỉ học sinh mới có thể tạo đánh giá
    if g.role != 'student':
        return jsonify({"message": "Chỉ học sinh mới có quyền đánh giá"}), 403
    
    student_id = g.student_id  # Lấy student_id từ token
    class_id = data.get('class_id')
    feedback_type = data.get('feedback_type')
    teacher_id = data.get('teacher_id')
    classroom_id = data.get('classroom_id')
    content = data.get('content')
    
    # Validation
    if not all([student_id, class_id, feedback_type, content]):
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    if feedback_type not in ['TEACHER', 'CLASSROOM']:
        return jsonify({"message": "Loại đánh giá không hợp lệ"}), 400
    
    if feedback_type == 'TEACHER' and not teacher_id:
        return jsonify({"message": "Thiếu thông tin giảng viên"}), 400
    
    if feedback_type == 'CLASSROOM' and not classroom_id:
        return jsonify({"message": "Thiếu thông tin phòng học"}), 400
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Kiểm tra giảng viên có dạy lớp không (nếu là đánh giá giảng viên)
    if feedback_type == 'TEACHER':
        teacher_in_class = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
        if not teacher_in_class:
            return jsonify({"message": "Giảng viên không dạy lớp này"}), 403
    
    # Kiểm tra học sinh đã đánh giá trong lớp này chưa
    if feedback_type == 'TEACHER':
        existing_feedback = Feedback.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            teacher_id=teacher_id,
            feedback_type='TEACHER'
        ).first()
        
        if existing_feedback:
            return jsonify({"message": "Bạn đã đánh giá giảng viên này trong lớp này"}), 409
    else:
        existing_feedback = Feedback.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            classroom_id=classroom_id,
            feedback_type='CLASSROOM'
        ).first()
        
        if existing_feedback:
            return jsonify({"message": "Bạn đã đánh giá phòng học này trong lớp này"}), 409
    
    # Lấy start_date và end_date từ bảng class và tính end_date + 7 ngày
    class_ = Class.query.get_or_404(class_id)
    start_date = class_.start_date
    end_date = class_.end_date
    
    # Kiểm tra thời gian có nằm trong khoảng cho phép đánh giá không
    current_date = datetime.now().date()
    feedback_end_date = class_.end_date + datetime.timedelta(days=7)
    
    if current_date < start_date:
        return jsonify({"message": "Chưa đến thời gian đánh giá"}), 403
    if current_date > feedback_end_date:
        return jsonify({"message": "Đã kết thúc thời gian đánh giá"}), 403
    
    # Dự đoán sentiment sử dụng model
    sentiment_label = prediction(content)
    sentiment_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    predicted_sentiment = sentiment_map[sentiment_label]
    
    new_feedback = Feedback(
        content=content,
        student_id=student_id,
        class_id=class_id,
        teacher_id=teacher_id if feedback_type == 'TEACHER' else None,
        classroom_id=classroom_id if feedback_type == 'CLASSROOM' else None,
        start_date=start_date,
        end_date=feedback_end_date,
        sentiment=predicted_sentiment,
        feedback_type=feedback_type
    )
    
    try:
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({"message": "Feedback created successfully"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {str(e)}"}), 400

@feedback_bp.route('/feedbacks', methods=['GET'])
@auth_required
def get_feedbacks():
    """Lấy danh sách đánh giá có thể lọc theo các tham số"""
    feedback_type = request.args.get('feedback_type')
    sentiment = request.args.get('sentiment')
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    classroom_id = request.args.get('classroom_id')
    
    # Xây dựng truy vấn với các bộ lọc
    query = Feedback.query
    
    # Nếu là admin: có thể xem tất cả feedback
    # Nếu là học sinh: chỉ xem được feedback của mình
    if g.role != 'admin':
        if g.role == 'student':
            query = query.filter_by(student_id=g.student_id)
        elif g.role == 'teacher':
            # Giảng viên chỉ xem được feedback về mình
            query = query.filter_by(teacher_id=g.teacher_id, feedback_type='TEACHER')
        else:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Áp dụng các bộ lọc
    if feedback_type:
        query = query.filter_by(feedback_type=feedback_type)
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    if student_id and g.role == 'admin':  # Chỉ admin mới có thể lọc theo student_id
        query = query.filter_by(student_id=student_id)
    if class_id:
        query = query.filter_by(class_id=class_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
    
    # Thực hiện truy vấn và trả về kết quả
    feedbacks = query.all()
    return jsonify([{
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "teacher_id": feedback.teacher_id,
        "classroom_id": feedback.classroom_id,
        "start_date": feedback.start_date.strftime('%Y-%m-%d') if feedback.start_date else None,
        "end_date": feedback.end_date.strftime('%Y-%m-%d') if feedback.end_date else None,
        "sentiment": feedback.sentiment,
        "feedback_type": feedback.feedback_type,
        "created_at": feedback.created_at
    } for feedback in feedbacks])

@feedback_bp.route('/feedbacks/<int:id>', methods=['GET'])
@auth_required
def get_feedback(id):
    """Lấy thông tin chi tiết của một đánh giá"""
    feedback = Feedback.query.get_or_404(id)
    
    # Kiểm tra quyền: admin xem được tất cả, học sinh chỉ xem được feedback của mình
    if g.role != 'admin':
        if g.role == 'student' and feedback.student_id != g.student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
        elif g.role == 'teacher' and (feedback.teacher_id != g.teacher_id or feedback.feedback_type != 'TEACHER'):
            return jsonify({"message": "Không có quyền truy cập"}), 403
        elif g.role not in ['student', 'teacher', 'admin']:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    return jsonify({
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "teacher_id": feedback.teacher_id,
        "classroom_id": feedback.classroom_id,
        "start_date": feedback.start_date.strftime('%Y-%m-%d') if feedback.start_date else None,
        "end_date": feedback.end_date.strftime('%Y-%m-%d') if feedback.end_date else None,
        "sentiment": feedback.sentiment,
        "feedback_type": feedback.feedback_type,
        "created_at": feedback.created_at
    })

@feedback_bp.route('/feedbacks/<int:id>', methods=['DELETE'])
@auth_required
def delete_feedback(id):
    """Xóa một đánh giá"""
    feedback = Feedback.query.get_or_404(id)
    
    # Chỉ admin mới có thể xóa feedback, hoặc học sinh xóa feedback của chính mình
    if g.role != 'admin':
        if g.role != 'student' or feedback.student_id != g.student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
        
        # Học sinh chỉ có thể xóa feedback trong khoảng thời gian nhất định (ví dụ: 24 giờ sau khi tạo)
        current_time = datetime.now()
        feedback_time = feedback.created_at
        time_diff = current_time - feedback_time
        
        if time_diff.total_seconds() > 24 * 60 * 60:  # 24 giờ
            return jsonify({"message": "Không thể xóa đánh giá sau 24 giờ"}), 403
    
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback deleted successfully"})

@feedback_bp.route('/feedbacks/student/<string:student_id>/classes/<int:class_id>/teachers', methods=['GET'])
@auth_required
def get_teachers_for_feedback(student_id, class_id):
    """Lấy danh sách giảng viên mà học sinh có thể đánh giá"""
    
    # Kiểm tra quyền: chỉ admin hoặc chính học sinh đó mới có thể xem
    if g.role != 'admin':
        if g.role != 'student' or g.student_id != student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Lấy danh sách giảng viên đã được đánh giá bởi học sinh này trong lớp này
    evaluated_teachers = db.session.query(Feedback.teacher_id).filter_by(
        student_id=student_id,
        class_id=class_id,
        feedback_type='TEACHER'
    ).all()
    
    evaluated_teacher_ids = [t.teacher_id for t in evaluated_teachers]
    
    # Lấy tất cả giảng viên trong lớp học
    class_teachers = ClassTeacher.query.filter_by(class_id=class_id).all()
    
    # Lọc ra các giảng viên chưa được đánh giá
    available_teachers = []
    
    for class_teacher in class_teachers:
        teacher = class_teacher.teacher
        if teacher.id not in evaluated_teacher_ids:
            available_teachers.append({
                "id": teacher.id,
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
                "email": teacher.email
            })
    
    return jsonify(available_teachers)

@feedback_bp.route('/feedbacks/student/<string:student_id>/classes/<int:class_id>/classrooms', methods=['GET'])
@auth_required
def get_classrooms_for_feedback(student_id, class_id):
    """Lấy danh sách phòng học mà học sinh có thể đánh giá"""
    
    # Kiểm tra quyền: chỉ admin hoặc chính học sinh đó mới có thể xem
    if g.role != 'admin':
        if g.role != 'student' or g.student_id != student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Lấy danh sách phòng học đã được đánh giá bởi học sinh này trong lớp này
    evaluated_classrooms = db.session.query(Feedback.classroom_id).filter_by(
        student_id=student_id,
        class_id=class_id,
        feedback_type='CLASSROOM'
    ).all()
    
    evaluated_classroom_ids = [c.classroom_id for c in evaluated_classrooms]
    
    # Lấy tất cả phòng học (đơn giản hóa, thực tế cần lấy từ class_schedule)
    # Giữ nguyên logic cũ tương tự như classroom_feedback.py
    from app.models.classroom import Classroom
    classrooms = Classroom.query.all()
    
    # Lọc ra các phòng học chưa được đánh giá
    available_classrooms = []
    
    for classroom in classrooms:
        if classroom.id not in evaluated_classroom_ids:
            available_classrooms.append({
                "id": classroom.id,
                "room_number": classroom.room_number,
                "capacity": classroom.capacity,
                "building_id": classroom.building_id
            })
    
    return jsonify(available_classrooms)