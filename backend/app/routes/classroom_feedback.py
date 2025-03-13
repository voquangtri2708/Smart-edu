from flask import Blueprint, request, jsonify
from app import db
from app.models.classroom_feedback import ClassroomFeedback
from app.models.classs import Class
from app.ml.pred import prediction
from datetime import timedelta

classroom_feedback_bp = Blueprint('classroom_feedback', __name__)

@classroom_feedback_bp.route('/classroom_feedbacks', methods=['POST'])
def create_classroom_feedback():
    data = request.get_json()
    content = data.get('content')
    
    # Dự đoán sentiment sử dụng model
    sentiment_label = prediction(content)
    sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
    predicted_sentiment = sentiment_map[sentiment_label]
    
    # Lấy start_date và end_date từ bảng class và tính end_date + 7 ngày
    class_ = Class.query.get_or_404(data['class_id'])
    start_date = class_.start_date
    end_date = class_.end_date + timedelta(days=7)
    
    new_feedback = ClassroomFeedback(
        content=content,
        student_id=data['student_id'],
        class_id=data['class_id'],
        classroom_id=data['classroom_id'],
        start_date=start_date,
        end_date=end_date,
        sentiment=predicted_sentiment
    )
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify({"message": "ClassroomFeedback created successfully"}), 201

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