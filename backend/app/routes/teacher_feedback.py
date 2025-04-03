from flask import Blueprint, request, jsonify
from app import db
from app.models.teacher_feedback import TeacherFeedback
from app.models.classs import Class
from app.models.class_student import ClassStudent
from app.models.class_teacher import ClassTeacher
from app.ml.pred import prediction
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

teacher_feedback_bp = Blueprint('teacher_feedback', __name__)

@teacher_feedback_bp.route('/teacher_feedbacks', methods=['POST'])
def create_teacher_feedback():
    data = request.get_json()
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    teacher_id = data.get('teacher_id')
    content = data.get('content')
    
    # Kiểm tra học sinh có thuộc lớp không
    student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
    if not student_in_class:
        return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
    
    # Kiểm tra giảng viên có dạy lớp không
    teacher_in_class = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
    if not teacher_in_class:
        return jsonify({"message": "Giảng viên không dạy lớp này"}), 403
    
    # Kiểm tra học sinh đã đánh giá giảng viên trong lớp này chưa
    existing_feedback = TeacherFeedback.query.filter_by(
        student_id=student_id,
        class_id=class_id,
        teacher_id=teacher_id
    ).first()
    
    if existing_feedback:
        return jsonify({"message": "Bạn đã đánh giá giảng viên này trong lớp này"}), 409
    
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
    
    new_feedback = TeacherFeedback(
        content=content,
        student_id=student_id,
        class_id=class_id,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date,
        sentiment=predicted_sentiment
    )
    
    try:
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({"message": "TeacherFeedback created successfully"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi: " + str(e)}), 400

@teacher_feedback_bp.route('/teacher_feedbacks', methods=['GET'])
def get_teacher_feedbacks():
    sentiment = request.args.get('sentiment')
    query = TeacherFeedback.query
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    feedbacks = query.all()
    return jsonify([{
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "teacher_id": feedback.teacher_id,
        "created_at": feedback.created_at,
        "start_date": feedback.start_date,
        "end_date": feedback.end_date,
        "sentiment": feedback.sentiment
    } for feedback in feedbacks])

@teacher_feedback_bp.route('/teacher_feedbacks/<int:id>', methods=['GET'])
def get_teacher_feedback(id):
    feedback = TeacherFeedback.query.get_or_404(id)
    return jsonify({
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "teacher_id": feedback.teacher_id,
        "created_at": feedback.created_at,
        "start_date": feedback.start_date,
        "end_date": feedback.end_date,
        "sentiment": feedback.sentiment
    })

@teacher_feedback_bp.route('/teacher_feedbacks/<int:id>', methods=['PUT'])
def update_teacher_feedback(id):
    data = request.get_json()
    feedback = TeacherFeedback.query.get_or_404(id)
    
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
    if 'teacher_id' in data:
        feedback.teacher_id = data['teacher_id']
    if 'start_date' in data:
        feedback.start_date = data['start_date']
    if 'end_date' in data:
        feedback.end_date = data['end_date']
    
    db.session.commit()
    return jsonify({"message": "TeacherFeedback updated successfully"})

@teacher_feedback_bp.route('/teacher_feedbacks/<int:id>', methods=['DELETE'])
def delete_teacher_feedback(id):
    feedback = TeacherFeedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "TeacherFeedback deleted successfully"})