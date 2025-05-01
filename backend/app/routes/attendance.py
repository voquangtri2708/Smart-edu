from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.classs import Class
from app.models.schedule import Schedule
from app.utils.auth import auth_required, admin_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendances', methods=['POST'])
@admin_required
def create_attendance():
    """Tạo mới một bản ghi điểm danh"""
    data = request.get_json()

    # Validate input
    if not data or 'student_id' not in data or 'class_id' not in data or 'schedule_id' not in data or 'status' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

    # Check if student, class, and schedule exist
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({"message": "Học sinh không tồn tại"}), 404

    class_ = Class.query.get(data['class_id'])
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404

    schedule = Schedule.query.get(data['schedule_id'])
    if not schedule:
        return jsonify({"message": "Lịch học không tồn tại"}), 404

    # Create new attendance record
    new_attendance = Attendance(
        student_id=data['student_id'],
        class_id=data['class_id'],
        schedule_id=data['schedule_id'],
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        status=data['status'],
        recorded_by=data.get('recorded_by'),
        notes=data.get('notes')
    )
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify({"message": "Attendance created successfully"}), 201

@attendance_bp.route('/attendances', methods=['GET'])
@auth_required
def get_attendances():
    """Lấy danh sách tất cả bản ghi điểm danh"""
    attendances = Attendance.query.all()
    return jsonify([{
        "id": attendance.id,
        "student_id": attendance.student_id,
        "class_id": attendance.class_id,
        "schedule_id": attendance.schedule_id,
        "start_time": attendance.start_time,
        "end_time": attendance.end_time,
        "status": attendance.status,
        "recorded_by": attendance.recorded_by,
        "notes": attendance.notes,
        "created_at": attendance.created_at,
        "updated_at": attendance.updated_at
    } for attendance in attendances])

@attendance_bp.route('/attendances/<int:id>', methods=['GET'])
@auth_required
def get_attendance(id):
    """Lấy thông tin chi tiết của một bản ghi điểm danh"""
    attendance = Attendance.query.get_or_404(id)
    return jsonify({
        "id": attendance.id,
        "student_id": attendance.student_id,
        "class_id": attendance.class_id,
        "schedule_id": attendance.schedule_id,
        "start_time": attendance.start_time,
        "end_time": attendance.end_time,
        "status": attendance.status,
        "recorded_by": attendance.recorded_by,
        "notes": attendance.notes,
        "created_at": attendance.created_at,
        "updated_at": attendance.updated_at
    })

@attendance_bp.route('/attendances/<int:id>', methods=['PUT'])
@admin_required
def update_attendance(id):
    """Cập nhật thông tin điểm danh"""
    data = request.get_json()
    attendance = Attendance.query.get_or_404(id)

    if 'status' in data:
        attendance.status = data['status']
    if 'start_time' in data:
        attendance.start_time = data['start_time']
    if 'end_time' in data:
        attendance.end_time = data['end_time']
    if 'notes' in data:
        attendance.notes = data['notes']

    db.session.commit()
    return jsonify({"message": "Attendance updated successfully"})

@attendance_bp.route('/attendances/<int:id>', methods=['DELETE'])
@admin_required
def delete_attendance(id):
    """Xóa một bản ghi điểm danh"""
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    return jsonify({"message": "Attendance deleted successfully"})