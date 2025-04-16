from flask import Blueprint, request, jsonify, g
from app.models.classs import Class
from datetime import datetime, timedelta
from app.utils.auth import auth_required

feedback_availability_bp = Blueprint('feedback_availability', __name__)

@feedback_availability_bp.route('/feedback-availability', methods=['GET'])
@auth_required
def check_feedback_availability():
    class_id = request.args.get('class_id')
    
    if not class_id:
        return jsonify({"message": "Class ID is required"}), 400
    
    class_ = Class.query.get(class_id)
    
    if not class_:
        return jsonify({"message": "Class not found"}), 404
    
    start_date = class_.start_date
    end_date = class_.end_date
    
    # Feedback is available from start_date to end_date + 7 days
    current_date = datetime.now().date()
    feedback_end_date = end_date + timedelta(days=7)
    
    is_available = current_date >= start_date and current_date <= feedback_end_date
    
    status = "available"
    if current_date < start_date:
        status = "upcoming"
    elif current_date > feedback_end_date:
        status = "expired"
    
    return jsonify({
        "class_id": class_id,
        "start_date": start_date.strftime('%Y-%m-%d') if start_date else None,
        "end_date": feedback_end_date.strftime('%Y-%m-%d') if feedback_end_date else None,
        "current_date": current_date.strftime('%Y-%m-%d'),
        "is_available": is_available,
        "status": status
    })