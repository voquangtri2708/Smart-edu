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

# Function to check time overlap between two schedules
def is_time_overlapping(start1, end1, start2, end2):
    """Check if two time periods overlap
    
    Args:
        start1, end1: Start and end time of first schedule
        start2, end2: Start and end time of second schedule
        
    Returns:
        bool: True if schedules overlap, False otherwise
    """
    # Case 1: start1 is during schedule 2
    if start1 >= start2 and start1 < end2:
        return True
    # Case 2: end1 is during schedule 2
    if end1 > start2 and end1 <= end2:
        return True
    # Case 3: schedule 1 completely overlaps schedule 2
    if start1 <= start2 and end1 >= end2:
        return True
    return False

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
    class_id = data['class_id']
    classroom_id = data['classroom_id']
    
    # Kiểm tra lớp học có tồn tại và không bị đánh dấu xóa
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({"error": "Lớp học không tồn tại"}), 404
    
    if class_obj.is_del:
        return jsonify({"error": "Không thể thêm lịch học cho lớp đã kết thúc"}), 400
    
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
    
    # 1. Check for conflicts within the same class - Prevent multiple schedules for the same class at the same time
    class_schedules = Schedule.query.filter(
        Schedule.class_id == class_id,
        Schedule.specific_date == specific_date
    ).all()
    
    for schedule in class_schedules:
        if is_time_overlapping(start_time, end_time, schedule.start_time, schedule.end_time):
            return jsonify({
                "error": "Lớp học này đã có lịch học khác vào cùng thời điểm này"
            }), 400
    
    # 2. Check for classroom conflicts - Ensure no other class uses this room at this time
    room_schedules = Schedule.query.filter(
        Schedule.classroom_id == classroom_id,
        Schedule.specific_date == specific_date
    ).all()
    
    for schedule in room_schedules:
        if is_time_overlapping(start_time, end_time, schedule.start_time, schedule.end_time):
            return jsonify({
                "error": "Phòng học đã được sử dụng bởi lớp khác vào cùng thời điểm này"
            }), 400
    
    # 3. Check for student conflicts - Students can't be in two classes at once
    # Get all students enrolled in this class
    students_in_class = ClassStudent.query.filter_by(class_id=class_id).all()
    student_ids = [s.student_id for s in students_in_class]
    
    if student_ids:  # Only check if there are students enrolled
        # Find all other classes these students are enrolled in
        other_classes = ClassStudent.query.filter(
            ClassStudent.student_id.in_(student_ids),
            ClassStudent.class_id != class_id
        ).all()
        other_class_ids = [c.class_id for c in other_classes]
        
        if other_class_ids:  # Only check if students are enrolled in other classes
            # Find schedules for those other classes on the same date
            conflict_schedules = Schedule.query.filter(
                Schedule.class_id.in_(other_class_ids),
                Schedule.specific_date == specific_date
            ).all()
            
            # Check for time conflicts
            for schedule in conflict_schedules:
                if is_time_overlapping(start_time, end_time, schedule.start_time, schedule.end_time):
                    # Find which students have this conflict
                    conflicted_students = ClassStudent.query.filter(
                        ClassStudent.class_id == schedule.class_id,
                        ClassStudent.student_id.in_(student_ids)
                    ).all()
                    conflicted_student_ids = [s.student_id for s in conflicted_students]
                    
                    return jsonify({
                        "error": f"Sinh viên đã có lịch học khác vào cùng thời điểm này",
                        "detail": f"{len(conflicted_student_ids)} sinh viên có lịch trùng với lớp {schedule.class_id}"
                    }), 400
    
    # 4. Check for teacher conflicts - Teachers can't teach two classes at once
    # Get all teachers for this class
    teachers_in_class = ClassTeacher.query.filter_by(class_id=class_id).all()
    teacher_ids = [t.teacher_id for t in teachers_in_class]
    
    if teacher_ids:  # Only check if there are teachers assigned
        # Find all other classes these teachers are teaching
        other_classes = ClassTeacher.query.filter(
            ClassTeacher.teacher_id.in_(teacher_ids),
            ClassTeacher.class_id != class_id
        ).all()
        other_class_ids = [c.class_id for c in other_classes]
        
        if other_class_ids:  # Only check if teachers teach other classes
            # Find schedules for those other classes on the same date
            conflict_schedules = Schedule.query.filter(
                Schedule.class_id.in_(other_class_ids),
                Schedule.specific_date == specific_date
            ).all()
            
            # Check for time conflicts
            for schedule in conflict_schedules:
                if is_time_overlapping(start_time, end_time, schedule.start_time, schedule.end_time):
                    # Find which teachers have this conflict
                    conflicted_teachers = ClassTeacher.query.filter(
                        ClassTeacher.class_id == schedule.class_id,
                        ClassTeacher.teacher_id.in_(teacher_ids)
                    ).all()
                    conflicted_teacher_ids = [t.teacher_id for t in conflicted_teachers]
                    
                    return jsonify({
                        "error": f"Giáo viên đã có lịch dạy khác vào cùng thời điểm này",
                        "detail": f"{len(conflicted_teacher_ids)} giáo viên có lịch trùng với lớp {schedule.class_id}"
                    }), 400
    
    # All checks passed, create the new schedule
    new_schedule = Schedule(
        class_id=class_id,
        classroom_id=classroom_id,
        day_of_week=day_of_week,
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
    """Lấy danh sách tất cả các lịch học với thông tin chi tiết"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
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
    
    # Lọc theo trạng thái is_del của lớp học
    if not include_deleted:
        query = query.filter(Class.is_del == False)
    
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
            "is_del": class_.is_del if class_ else False,
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
        "is_del": class_.is_del if class_ else False,
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
    
    # Capture current values to use if not updated
    start_time = schedule.start_time
    end_time = schedule.end_time
    classroom_id = schedule.classroom_id
    specific_date = schedule.specific_date
    class_id = schedule.class_id
    
    # Update values with new data if provided
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
        
    if 'class_id' in data:
        class_id = data['class_id']
        
    # Kiểm tra lớp học có tồn tại và không bị đánh dấu xóa
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({"error": "Lớp học không tồn tại"}), 404
    
    if class_obj.is_del:
        return jsonify({"error": "Không thể cập nhật lịch học cho lớp đã kết thúc"}), 400
    
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
    
    # 1. Check for conflicts within the same class - Prevent multiple schedules for the same class at the same time
    class_schedules = Schedule.query.filter(
        Schedule.id != id,  # Exclude current schedule
        Schedule.class_id == class_id,
        Schedule.specific_date == specific_date
    ).all()
    
    for existing in class_schedules:
        if is_time_overlapping(start_time, end_time, existing.start_time, existing.end_time):
            return jsonify({
                "error": "Lớp học này đã có lịch học khác vào cùng thời điểm này"
            }), 400
    
    # 2. Check for classroom conflicts - Ensure no other class uses this room at this time
    room_schedules = Schedule.query.filter(
        Schedule.id != id,  # Exclude current schedule
        Schedule.classroom_id == classroom_id,
        Schedule.specific_date == specific_date
    ).all()
    
    for existing in room_schedules:
        if is_time_overlapping(start_time, end_time, existing.start_time, existing.end_time):
            return jsonify({
                "error": "Phòng học đã được sử dụng bởi lớp khác vào cùng thời điểm này"
            }), 400
    
    # 3. Check for student conflicts - Students can't be in two classes at once
    # Get all students enrolled in this class
    students_in_class = ClassStudent.query.filter_by(class_id=class_id).all()
    student_ids = [s.student_id for s in students_in_class]
    
    if student_ids:  # Only check if there are students enrolled
        # Find all other classes these students are enrolled in
        other_classes = ClassStudent.query.filter(
            ClassStudent.student_id.in_(student_ids),
            ClassStudent.class_id != class_id
        ).all()
        other_class_ids = [c.class_id for c in other_classes]
        
        if other_class_ids:  # Only check if students are enrolled in other classes
            # Find schedules for those other classes on the same date
            conflict_schedules = Schedule.query.filter(
                Schedule.id != id,  # Exclude current schedule
                Schedule.class_id.in_(other_class_ids),
                Schedule.specific_date == specific_date
            ).all()
            
            # Check for time conflicts
            for existing in conflict_schedules:
                if is_time_overlapping(start_time, end_time, existing.start_time, existing.end_time):
                    # Find which students have this conflict
                    conflicted_students = ClassStudent.query.filter(
                        ClassStudent.class_id == existing.class_id,
                        ClassStudent.student_id.in_(student_ids)
                    ).all()
                    conflicted_student_ids = [s.student_id for s in conflicted_students]
                    
                    return jsonify({
                        "error": f"Sinh viên đã có lịch học khác vào cùng thời điểm này",
                        "detail": f"{len(conflicted_student_ids)} sinh viên có lịch trùng với lớp {existing.class_id}"
                    }), 400
    
    # 4. Check for teacher conflicts - Teachers can't teach two classes at once
    # Get all teachers for this class
    teachers_in_class = ClassTeacher.query.filter_by(class_id=class_id).all()
    teacher_ids = [t.teacher_id for t in teachers_in_class]
    
    if teacher_ids:  # Only check if there are teachers assigned
        # Find all other classes these teachers are teaching
        other_classes = ClassTeacher.query.filter(
            ClassTeacher.teacher_id.in_(teacher_ids),
            ClassTeacher.class_id != class_id
        ).all()
        other_class_ids = [c.class_id for c in other_classes]
        
        if other_class_ids:  # Only check if teachers teach other classes
            # Find schedules for those other classes on the same date
            conflict_schedules = Schedule.query.filter(
                Schedule.id != id,  # Exclude current schedule
                Schedule.class_id.in_(other_class_ids),
                Schedule.specific_date == specific_date
            ).all()
            
            # Check for time conflicts
            for existing in conflict_schedules:
                if is_time_overlapping(start_time, end_time, existing.start_time, existing.end_time):
                    # Find which teachers have this conflict
                    conflicted_teachers = ClassTeacher.query.filter(
                        ClassTeacher.class_id == existing.class_id,
                        ClassTeacher.teacher_id.in_(teacher_ids)
                    ).all()
                    conflicted_teacher_ids = [t.teacher_id for t in conflicted_teachers]
                    
                    return jsonify({
                        "error": f"Giáo viên đã có lịch dạy khác vào cùng thời điểm này",
                        "detail": f"{len(conflicted_teacher_ids)} giáo viên có lịch trùng với lớp {existing.class_id}"
                    }), 400
    
    # All checks passed, update the schedule
    if 'class_id' in data:
        schedule.class_id = class_id
    if 'classroom_id' in data:
        schedule.classroom_id = classroom_id
    schedule.day_of_week = day_of_week  # Always update day_of_week based on date
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

@schedule_bp.route('/class/<int:class_id>/schedules', methods=['GET'])
@auth_required
def get_class_schedules(class_id):
    """Lấy danh sách lịch học của một lớp học cụ thể"""
    try:
        # Kiểm tra lớp học có tồn tại và không bị đánh dấu xóa
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Lớp học không tồn tại"}), 404
        
        # Lấy ngày hiện tại
        current_date = date.today()
        
        # Kiểm tra nếu có tham số specific_date trong query
        specific_date_str = request.args.get('specific_date')
        if specific_date_str:
            try:
                # Nếu có tham số, sử dụng ngày từ tham số
                current_date = datetime.strptime(specific_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass  # Sử dụng ngày hiện tại nếu định dạng không hợp lệ
        
        # Lấy tất cả lịch học của lớp này VÀ ngày hiện tại
        schedules = Schedule.query.filter(
            Schedule.class_id == class_id,
            Schedule.specific_date == current_date
        ).all()
        
        result = []
        for schedule in schedules:
            # Thông tin phòng học
            classroom = Classroom.query.get(schedule.classroom_id)
            building = Building.query.get(classroom.building_id) if classroom else None
            campus = Campus.query.get(building.campus_id) if building else None
            
            # Chuyển đổi từ enum sang tên đầy đủ của ngày trong tuần
            day_names = {
                'MON': 'Thứ hai',
                'TUE': 'Thứ ba',
                'WED': 'Thứ tư',
                'THU': 'Thứ năm',
                'FRI': 'Thứ sáu',
                'SAT': 'Thứ bảy',
                'SUN': 'Chủ nhật'
            }
            
            result.append({
                "id": schedule.id,
                "class_id": schedule.class_id,
                "day_of_week": day_names.get(schedule.day_of_week, schedule.day_of_week),
                "start_time": format_time(schedule.start_time),
                "end_time": format_time(schedule.end_time),
                "specific_date": format_date(schedule.specific_date),
                "classroom_id": schedule.classroom_id,
                "room_number": classroom.room_number if classroom else None,
                "building_id": building.id if building else None,
                "building_name": building.name if building else None,
                "campus_id": campus.id if campus else None,
                "campus_name": campus.name if campus else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500