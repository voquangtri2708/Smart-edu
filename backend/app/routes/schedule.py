from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from app.models.classroom import Classroom
from app.models.classs import Class
from datetime import datetime, time
from sqlalchemy import or_, and_

schedule_bp = Blueprint('schedule', __name__)

def check_schedule_conflict(start_time, end_time, day_of_week, classroom_id, specific_date=None, exclude_id=None):
    """Kiểm tra xung đột lịch học"""
    query = Schedule.query.filter(
        Schedule.classroom_id == classroom_id,
        Schedule.day_of_week == day_of_week
    )
    
    if specific_date:
        query = query.filter(Schedule.specific_date == specific_date)
    
    if exclude_id:
        query = query.filter(Schedule.id != exclude_id)
        
    conflicts = query.filter(
        or_(
            and_(start_time >= Schedule.start_time, start_time < Schedule.end_time),
            and_(end_time > Schedule.start_time, end_time <= Schedule.end_time),
            and_(start_time <= Schedule.start_time, end_time >= Schedule.end_time)
        )
    ).all()
    
    return len(conflicts) > 0

@schedule_bp.route('/schedules', methods=['POST'])
def create_schedule():
    try:
        data = request.get_json()
        
        # Kiểm tra lớp học và phòng học tồn tại
        class_ = Class.query.get_or_404(data['class_id'])
        classroom = Classroom.query.get_or_404(data['classroom_id'])
        
        # Parse thời gian
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        specific_date = datetime.strptime(data['specific_date'], '%Y-%m-%d').date() if 'specific_date' in data else None
        
        # Kiểm tra xung đột
        if check_schedule_conflict(start_time, end_time, data['day_of_week'], data['classroom_id'], specific_date):
            return jsonify({"message": "Lịch học bị trùng"}), 409
            
        new_schedule = Schedule(
            start_time=start_time,
            end_time=end_time,
            day_of_week=data['day_of_week'],
            specific_date=specific_date,
            class_id=data['class_id'],
            classroom_id=data['classroom_id']
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        return jsonify(new_schedule.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@schedule_bp.route('/schedules', methods=['GET'])
def get_schedules():
    class_id = request.args.get('class_id', type=int)
    classroom_id = request.args.get('classroom_id', type=int)
    
    query = Schedule.query
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
        
    schedules = query.all()
    return jsonify([schedule.to_dict(include_relations=True) for schedule in schedules])

@schedule_bp.route('/schedules/<int:id>', methods=['GET'])
def get_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    return jsonify(schedule.to_dict(include_relations=True))

@schedule_bp.route('/schedules/<int:id>', methods=['PUT'])
def update_schedule(id):
    try:
        schedule = Schedule.query.get_or_404(id)
        data = request.get_json()
        
        start_time = datetime.strptime(data['start_time'], '%H:%M').time() if 'start_time' in data else schedule.start_time
        end_time = datetime.strptime(data['end_time'], '%H:%M').time() if 'end_time' in data else schedule.end_time
        day_of_week = data.get('day_of_week', schedule.day_of_week)
        classroom_id = data.get('classroom_id', schedule.classroom_id)
        specific_date = datetime.strptime(data['specific_date'], '%Y-%m-%d').date() if 'specific_date' in data else schedule.specific_date
        
        # Kiểm tra xung đột
        if check_schedule_conflict(start_time, end_time, day_of_week, classroom_id, specific_date, id):
            return jsonify({"message": "Lịch học bị trùng"}), 409
            
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.day_of_week = day_of_week
        schedule.specific_date = specific_date
        schedule.classroom_id = classroom_id
        if 'class_id' in data:
            schedule.class_id = data['class_id']
            
        db.session.commit()
        return jsonify(schedule.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@schedule_bp.route('/schedules/<int:id>', methods=['DELETE'])
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Schedule deleted successfully"})
