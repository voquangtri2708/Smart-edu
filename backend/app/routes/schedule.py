from flask import Blueprint, request, jsonify, g
from app import db
from app.models.schedule import Schedule
from app.models.class_student import ClassStudent
from app.models.class_teacher import ClassTeacher
from app.models.classroom import Classroom
from app.models.building import Building
from app.models.campus import Campus
from app.models.classs import Class
from app.models.subject import Subject
from app.utils.auth import auth_required, admin_required
from datetime import datetime, time, date
from sqlalchemy import and_, or_

schedule_bp = Blueprint('schedule', __name__)

def format_time(t):
    return t.strftime('%H:%M') if t else None

def format_date(d):
    return d.strftime('%Y-%m-%d') if d else None

# Map số ngày trong tuần sang ENUM
DAY_MAP = {
    1: 'MON',
    2: 'TUE',
    3: 'WED',
    4: 'THU',
    5: 'FRI',
    6: 'SAT',
    7: 'SUN'
}

# Map ENUM ngày sang số
DAY_NUMBER = {
    'MON': 1,
    'TUE': 2,
    'WED': 3,
    'THU': 4,
    'FRI': 5,
    'SAT': 6,
    'SUN': 7
}

# Admin: Create a new schedule
@schedule_bp.route('/schedules', methods=['POST'])
@auth_required
@admin_required
def create_schedule():
    data = request.get_json()
    
    # Parse times
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    
    # Validate end_time is after start_time
    if end_time <= start_time:
        return jsonify({"error": "Thời gian kết thúc phải sau thời gian bắt đầu"}), 400
    
    # Parse specific_date - Bây giờ là bắt buộc
    if 'specific_date' not in data or not data['specific_date']:
        return jsonify({"error": "Ngày cụ thể là bắt buộc"}), 400

    specific_date = datetime.strptime(data['specific_date'], '%Y-%m-%d').date()
    
    # Tính day_of_week từ specific_date
    day_map = {
        0: 'MON',  # Monday
        1: 'TUE', 
        2: 'WED',
        3: 'THU',
        4: 'FRI',
        5: 'SAT',
        6: 'SUN'  # Sunday
    }
    day_of_week = day_map[specific_date.weekday()]
    
    # Check for schedule conflicts in the same classroom
    classroom_id = data['classroom_id']
    existing_schedules = Schedule.query.filter(
        Schedule.classroom_id == classroom_id,
        Schedule.specific_date == specific_date
    ).all()
    
    # Check for time conflicts manually
    conflicts = []
    for schedule in existing_schedules:
        # Case 1: New start time is during an existing schedule
        if start_time >= schedule.start_time and start_time < schedule.end_time:
            conflicts.append(schedule)
        # Case 2: New end time is during an existing schedule
        elif end_time > schedule.start_time and end_time <= schedule.end_time:
            conflicts.append(schedule)
        # Case 3: New schedule completely overlaps an existing schedule
        elif start_time <= schedule.start_time and end_time >= schedule.end_time:
            conflicts.append(schedule)
    
    if conflicts:
        return jsonify({"error": "Lịch học bị trùng với lịch học khác trong cùng phòng học"}), 400
    
    new_schedule = Schedule(
        class_id=data['class_id'],
        classroom_id=classroom_id,
        day_of_week=day_of_week,  # Đã được tính từ specific_date
        start_time=start_time,
        end_time=end_time,
        specific_date=specific_date
    )
    db.session.add(new_schedule)
    db.session.commit()
    return jsonify({"message": "Lịch học đã được tạo thành công", "id": new_schedule.id}), 201

# Get all schedules (Admin) or filtered schedules (Teacher/Student)
@schedule_bp.route('/schedules', methods=['GET'])
@auth_required
def get_schedules():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent performance issues
    if per_page > 100:
        per_page = 100
    
    # Base query with joins to get related data
    query = db.session.query(
        Schedule,
        Class,
        Subject,
        Classroom,
        Building,
        Campus
    ).join(
        Class, Schedule.class_id == Class.id
    ).join(
        Subject, Class.subject_id == Subject.id, isouter=True
    ).join(
        Classroom, Schedule.classroom_id == Classroom.id
    ).join(
        Building, Classroom.building_id == Building.id, isouter=True
    ).join(
        Campus, Building.campus_id == Campus.id, isouter=True
    )
    
    # Filter based on user role
    if g.role == 'student':
        # For students, only show schedules for classes they are enrolled in
        student_classes = db.session.query(ClassStudent.class_id).filter_by(student_id=g.student_id).all()
        student_class_ids = [c[0] for c in student_classes]
        query = query.filter(Schedule.class_id.in_(student_class_ids))
    elif g.role == 'teacher':
        # For teachers, only show schedules for classes they teach
        teacher_classes = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        teacher_class_ids = [c[0] for c in teacher_classes]
        query = query.filter(Schedule.class_id.in_(teacher_class_ids))
    
    # Optional filters
    class_id = request.args.get('class_id', type=int)
    if class_id:
        query = query.filter(Schedule.class_id == class_id)
    
    classroom_id = request.args.get('classroom_id', type=int)
    if classroom_id:
        query = query.filter(Schedule.classroom_id == classroom_id)
    
    # Filter by specific date if provided
    specific_date_str = request.args.get('specific_date')
    if specific_date_str:
        try:
            specific_date = datetime.strptime(specific_date_str, '%Y-%m-%d').date()
            query = query.filter(Schedule.specific_date == specific_date)
        except ValueError:
            pass  # Ignore invalid date format
    
    # Filter by date range if provided
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Schedule.specific_date.between(start_date, end_date))
        except ValueError:
            pass  # Ignore invalid date format
    
    # Order by specific_date and start_time for natural schedule display
    query = query.order_by(Schedule.specific_date, Schedule.start_time)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination manually since we're using a complex query
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # Format results
    result_items = []
    for schedule, class_, subject, classroom, building, campus in items:
        item = {
            "id": schedule.id,
            "class_id": schedule.class_id,
            "classroom_id": schedule.classroom_id,
            "day_of_week": schedule.day_of_week,
            "day_number": DAY_NUMBER.get(schedule.day_of_week, 0),
            "start_time": format_time(schedule.start_time),
            "end_time": format_time(schedule.end_time),
            "specific_date": format_date(schedule.specific_date),
            # Class and subject information
            "class_code": class_.code if class_ else None,
            "subject_id": subject.id if subject else None,
            "subject_code": subject.code if subject else None,
            "subject_name": subject.name if subject else None,
            # Classroom, building and campus information
            "classroom_number": classroom.room_number if classroom else None,
            "building_id": building.id if building else None,
            "building_name": building.name if building else None,
            "campus_id": campus.id if campus else None,
            "campus_name": campus.name if campus else None
        }
        result_items.append(item)
    
    # Calculate pagination values
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return jsonify({
        'items': result_items,
        'pagination': {
            'total': total,
            'pages': total_pages,
            'page': page,
            'per_page': per_page,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

# Get a specific schedule
@schedule_bp.route('/schedules/<int:id>', methods=['GET'])
@auth_required
def get_schedule(id):
    # Query schedule with all related information
    result = db.session.query(
        Schedule,
        Class,
        Subject,
        Classroom,
        Building,
        Campus
    ).join(
        Class, Schedule.class_id == Class.id
    ).join(
        Subject, Class.subject_id == Subject.id, isouter=True
    ).join(
        Classroom, Schedule.classroom_id == Classroom.id
    ).join(
        Building, Classroom.building_id == Building.id, isouter=True
    ).join(
        Campus, Building.campus_id == Campus.id, isouter=True
    ).filter(Schedule.id == id).first()
    
    if not result:
        return jsonify({"error": "Lịch học không tồn tại"}), 404
    
    schedule, class_, subject, classroom, building, campus = result
    
    # Check if the user has permission to view this schedule
    if g.role == 'student':
        student_classes = db.session.query(ClassStudent.class_id).filter_by(student_id=g.student_id).all()
        student_class_ids = [c[0] for c in student_classes]
        if schedule.class_id not in student_class_ids:
            return jsonify({"error": "Bạn không có quyền xem lịch học này"}), 403
    elif g.role == 'teacher':
        teacher_classes = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        teacher_class_ids = [c[0] for c in teacher_classes]
        if schedule.class_id not in teacher_class_ids:
            return jsonify({"error": "Bạn không có quyền xem lịch học này"}), 403
    
    # Format the response with all the additional information
    return jsonify({
        "id": schedule.id,
        "class_id": schedule.class_id,
        "classroom_id": schedule.classroom_id,
        "day_of_week": schedule.day_of_week,
        "day_number": DAY_NUMBER.get(schedule.day_of_week, 0),
        "start_time": format_time(schedule.start_time),
        "end_time": format_time(schedule.end_time),
        "specific_date": format_date(schedule.specific_date),
        # Class and subject information
        "class_code": class_.code if class_ else None,
        "subject_id": subject.id if subject else None,
        "subject_code": subject.code if subject else None,
        "subject_name": subject.name if subject else None,
        # Classroom, building and campus information
        "classroom_number": classroom.room_number if classroom else None,
        "building_id": building.id if building else None,
        "building_name": building.name if building else None,
        "campus_id": campus.id if campus else None,
        "campus_name": campus.name if campus else None
    })

# Update a schedule (admin only)
@schedule_bp.route('/schedules/<int:id>', methods=['PUT'])
@auth_required
@admin_required
def update_schedule(id):
    data = request.get_json()
    schedule = Schedule.query.get_or_404(id)
    
    start_time = schedule.start_time
    end_time = schedule.end_time
    classroom_id = schedule.classroom_id
    specific_date = schedule.specific_date
    
    if 'start_time' in data:
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    if 'end_time' in data:
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
    if 'specific_date' in data:
        if not data['specific_date']:
            return jsonify({"error": "Ngày cụ thể là bắt buộc"}), 400
        specific_date = datetime.strptime(data['specific_date'], '%Y-%m-%d').date()
            
    if 'classroom_id' in data:
        classroom_id = data['classroom_id']
    
    # Validate end_time is after start_time
    if end_time <= start_time:
        return jsonify({"error": "Thời gian kết thúc phải sau thời gian bắt đầu"}), 400
    
    # Tính day_of_week từ specific_date
    day_map = {
        0: 'MON',  # Monday
        1: 'TUE', 
        2: 'WED',
        3: 'THU',
        4: 'FRI',
        5: 'SAT',
        6: 'SUN'  # Sunday
    }
    day_of_week = day_map[specific_date.weekday()]
    
    # Check for schedule conflicts in the same classroom (excluding this schedule)
    existing_schedules = Schedule.query.filter(
        Schedule.id != id,
        Schedule.classroom_id == classroom_id,
        Schedule.specific_date == specific_date
    ).all()
    
    # Check for time conflicts manually
    conflicts = []
    for existing in existing_schedules:
        # Case 1: New start time is during an existing schedule
        if start_time >= existing.start_time and start_time < existing.end_time:
            conflicts.append(existing)
        # Case 2: New end time is during an existing schedule
        elif end_time > existing.start_time and end_time <= existing.end_time:
            conflicts.append(existing)
        # Case 3: New schedule completely overlaps an existing schedule
        elif start_time <= existing.start_time and end_time >= existing.end_time:
            conflicts.append(existing)
    
    if conflicts:
        return jsonify({"error": "Lịch học bị trùng với lịch học khác trong cùng phòng học"}), 400
    
    # Update fields
    if 'class_id' in data:
        schedule.class_id = data['class_id']
    if 'classroom_id' in data:
        schedule.classroom_id = classroom_id
    schedule.day_of_week = day_of_week  # Luôn cập nhật day_of_week
    if 'start_time' in data:
        schedule.start_time = start_time
    if 'end_time' in data:
        schedule.end_time = end_time
    if 'specific_date' in data:
        schedule.specific_date = specific_date
    
    db.session.commit()
    return jsonify({"message": "Lịch học đã được cập nhật thành công"})

# Delete a schedule (admin only)
@schedule_bp.route('/schedules/<int:id>', methods=['DELETE'])
@auth_required
@admin_required
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Lịch học đã được xóa thành công"}) 