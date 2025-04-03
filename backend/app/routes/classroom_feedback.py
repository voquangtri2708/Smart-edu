from flask import Blueprint, request, jsonify
from app import db
from app.models.classroom_feedback import ClassroomFeedback
from app.models.classs import Class
from app.models.class_student import ClassStudent
from app.models.classroom import Classroom
from app.ml.pred import prediction
from datetime import datetime, timedelta  # Thêm datetime
from sqlalchemy.exc import IntegrityError

classroom_feedback_bp = Blueprint('classroom_feedback', __name__)

@classroom_feedback_bp.route('/classroom_feedbacks', methods=['POST'])
def create_classroom_feedback():
    data = request.get_json()
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    classroom_id = data.get('classroom_id')
    content = data.get('content')
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Kiểm tra phòng học có được sử dụng cho lớp không (giả định có liên kết class_schedule)
    # Trong thực tế cần kiểm tra class_schedule để xác minh phòng học được dùng cho lớp này
    
    # Kiểm tra học sinh đã đánh giá phòng học trong lớp này chưa
    existing_feedback = ClassroomFeedback.query.filter_by(
        student_id=student_id,
        class_id=class_id,
        classroom_id=classroom_id
    ).first()
    
    if existing_feedback:
        return jsonify({"message": "Bạn đã đánh giá phòng học này trong lớp này"}), 409
    
    # Lấy start_date và end_date từ bảng class và tính end_date + 7 ngày
    class_ = Class.query.get_or_404(class_id)
    start_date = class_.start_date
    end_date = class_.end_date + timedelta(days=7)
    
    # Kiểm tra thời gian có nằm trong khoảng cho phép đánh giá không
    current_date = datetime.now().date()
    if current_date < start_date:
        return jsonify({"message": "Chưa đến thời gian đánh giá"}), 403
    if current_date > end_date:
        return jsonify({"message": "Đã kết thúc thời gian đánh giá"}), 403
    
    # Dự đoán sentiment sử dụng model
    sentiment_label = prediction(content)
    sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
    predicted_sentiment = sentiment_map[sentiment_label]
    
    new_feedback = ClassroomFeedback(
        content=content,
        student_id=student_id,
        class_id=class_id,
        classroom_id=classroom_id,
        start_date=start_date,
        end_date=end_date,
        sentiment=predicted_sentiment
    )
    
    try:
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({"message": "ClassroomFeedback created successfully"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi: " + str(e)}), 400

@classroom_feedback_bp.route('/classroom_feedbacks', methods=['GET'])
def get_classroom_feedbacks():
    feedbacks = ClassroomFeedback.query.all()
    return jsonify([{
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "classroom_id": feedback.classroom_id,
        "created_at": feedback.created_at,
        "start_date": feedback.start_date,
        "end_date": feedback.end_date,
        "sentiment": feedback.sentiment
    } for feedback in feedbacks])

@classroom_feedback_bp.route('/classroom_feedbacks/<int:id>', methods=['GET'])
def get_classroom_feedback(id):
    feedback = ClassroomFeedback.query.get_or_404(id)
    return jsonify({
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "classroom_id": feedback.classroom_id,
        "created_at": feedback.created_at,
        "start_date": feedback.start_date,
        "end_date": feedback.end_date,
        "sentiment": feedback.sentiment
    })

@classroom_feedback_bp.route('/classroom_feedbacks/<int:id>', methods=['PUT'])
def update_classroom_feedback(id):
    data = request.get_json()
    feedback = ClassroomFeedback.query.get_or_404(id)
    
    if 'content' in data:
        feedback.content = data['content']
        # Dự đoán sentiment sử dụng model
        sentiment_label = prediction(feedback.content)
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        feedback.sentiment = sentiment_map[sentiment_label]
    if 'student_id' in data:
        feedback.student_id = data['student_id']
    if 'class_id' in data:
        feedback.class_id = data['class_id']
    if 'classroom_id' in data:
        feedback.classroom_id = data['classroom_id']
    if 'start_date' in data:
        feedback.start_date = data['start_date']
    if 'end_date' in data:
        feedback.end_date = data['end_date']
    
    db.session.commit()
    return jsonify({"message": "ClassroomFeedback updated successfully"})

@classroom_feedback_bp.route('/classroom_feedbacks/<int:id>', methods=['DELETE'])
def delete_classroom_feedback(id):
    feedback = ClassroomFeedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "ClassroomFeedback deleted successfully"})

@classroom_feedback_bp.route('/classroom_feedbacks/student/<string:student_id>/classes/<int:class_id>/classrooms', methods=['GET'])
def get_classrooms_for_feedback(student_id, class_id):
    """Lấy danh sách phòng học mà học sinh có thể đánh giá"""
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Thực tế cần lấy từ class_schedule
    # Ở đây để đơn giản, giả sử có danh sách phòng học gán cho lớp
    # Trong triển khai thực tế, lấy từ bảng class_schedule
    
    # Lấy danh sách phòng học đã được đánh giá bởi học sinh này trong lớp này
    evaluated_classrooms = db.session.query(ClassroomFeedback.classroom_id).filter_by(
        student_id=student_id,
        class_id=class_id
    ).all()
    
    evaluated_classroom_ids = [c.classroom_id for c in evaluated_classrooms]
    
    # Lấy tất cả phòng học (đơn giản hóa, thực tế cần lấy từ class_schedule)
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