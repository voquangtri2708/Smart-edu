from flask import Blueprint, request, jsonify
from app import db
from app.models.feedback import Feedback
from app.ml.pred import prediction

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedbacks', methods=['POST'])
def create_feedback():
    data = request.get_json()
    content = data.get('content')
    
    # Dự đoán sentiment sử dụng model
    sentiment_label = prediction(content)
    sentiment_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
    predicted_sentiment = sentiment_map[sentiment_label]
    
    new_feedback = Feedback(
        content=content,
        student_id=data['student_id'],
        classroom_id=data.get('classroom_id'),
        teacher_id=data.get('teacher_id'),
        sentiment=predicted_sentiment
    )
    db.session.add(new_feedback)
    db.session.commit()
    
    return jsonify({
        "message": "Feedback created successfully",
        "feedback": {
            "id": new_feedback.id,
            "content": new_feedback.content,
            "sentiment": new_feedback.sentiment,
            "created_at": new_feedback.created_at
        }
    }), 201

@feedback_bp.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    feedbacks = Feedback.query.all()
    return jsonify([{
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "classroom_id": feedback.classroom_id,
        "teacher_id": feedback.teacher_id,
        "created_at": feedback.created_at,
        "updated_at": feedback.updated_at,
        "sentiment": feedback.sentiment
    } for feedback in feedbacks])

@feedback_bp.route('/feedbacks/<int:id>', methods=['GET'])
def get_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    return jsonify({
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "classroom_id": feedback.classroom_id,
        "teacher_id": feedback.teacher_id,
        "created_at": feedback.created_at,
        "updated_at": feedback.updated_at,
        "sentiment": feedback.sentiment
    })

# @feedback_bp.route('/feedbacks/<int:id>', methods=['PUT'])
# def update_feedback(id):
#     data = request.get_json()
#     feedback = Feedback.query.get_or_404(id)
    
#     if 'content' in data:
#         feedback.content = data['content']
#     if 'student_id' in data:
#         feedback.student_id = data['student_id']
#     if 'classroom_id' in data:
#         feedback.classroom_id = data['classroom_id']
#     if 'teacher_id' in data:
#         feedback.teacher_id = data['teacher_id']
#     if 'sentiment' in data:
#         feedback.sentiment = data['sentiment']
    
#     db.session.commit()
#     return jsonify({"message": "Feedback updated successfully"})

@feedback_bp.route('/feedbacks/<int:id>', methods=['DELETE'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback deleted successfully"})