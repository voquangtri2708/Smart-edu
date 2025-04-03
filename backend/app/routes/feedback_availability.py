from flask import Blueprint, jsonify
from app.models.classs import Class
from datetime import datetime, timedelta

feedback_availability_bp = Blueprint('feedback_availability', __name__)

@feedback_availability_bp.route('/feedback_availability/<int:class_id>', methods=['GET'])
def check_feedback_availability(class_id):
    """Kiểm tra xem lớp học có trong thời gian đánh giá không"""
    class_ = Class.query.get_or_404(class_id)
    
    start_date = class_.start_date
    end_date = class_.end_date + timedelta(days=7)
    current_date = datetime.now().date()
    
    can_feedback = start_date <= current_date <= end_date
    
    return jsonify({
        "class_id": class_id,
        "start_date": start_date.strftime('%Y-%m-%d') if start_date else None,
        "end_date": end_date.strftime('%Y-%m-%d') if end_date else None,
        "current_date": current_date.strftime('%Y-%m-%d'),
        "can_feedback": can_feedback,
        "status": "available" if can_feedback else ("upcoming" if current_date < start_date else "expired")
    })