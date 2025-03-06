from flask import Blueprint, request, jsonify
from app import db
from app.models.feedback import Feedback

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedbacks', methods=['POST'])
def create_feedback():
    data = request.get_json()
    new_feedback = Feedback(
        content=data.get('content'),
        student_id=data['student_id'],
        classroom_id=data['classroom_id'],
        teacher_id=data['teacher_id'],
        sentiment=data.get('sentiment', 'Trung lập')
    )
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify({"message": "Feedback created successfully"}), 201

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

@feedback_bp.route('/feedbacks/<int:id>', methods=['PUT'])
def update_feedback(id):
    data = request.get_json()
    feedback = Feedback.query.get_or_404(id)
    
    if 'content' in data:
        feedback.content = data['content']
    if 'student_id' in data:
        feedback.student_id = data['student_id']
    if 'classroom_id' in data:
        feedback.classroom_id = data['classroom_id']
    if 'teacher_id' in data:
        feedback.teacher_id = data['teacher_id']
    if 'sentiment' in data:
        feedback.sentiment = data['sentiment']
    
    db.session.commit()
    return jsonify({"message": "Feedback updated successfully"})

@feedback_bp.route('/feedbacks/<int:id>', methods=['DELETE'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback deleted successfully"})