from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.classs import Class
from app.models.schedule import Schedule
from app.models.class_student import ClassStudent
from app.utils.auth import auth_required, admin_required, get_current_user
from app.ml.faces import encode_face_from_base64, check_face
from datetime import datetime, timedelta
import ipaddress
import socket

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendances', methods=['POST'])
@auth_required
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
@auth_required
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

@attendance_bp.route('/teacher/create-attendance-session', methods=['POST'])
@auth_required
def create_attendance_session():
    """
    API để giáo viên tạo phiên điểm danh cho một lớp học
    
    Input: {
        "class_id": int,          # ID của lớp học
        "schedule_id": int,       # ID của lịch học
        "start_time": datetime,   # Thời gian bắt đầu điểm danh (ISO format)
        "end_time": datetime,     # Thời gian kết thúc điểm danh (ISO format)
        "notes": string,          # Ghi chú (không bắt buộc)
        "public_ip": string       # IP public của giáo viên (không bắt buộc)
    }
    """
    data = request.get_json()
    current_user = get_current_user()
    
    # Chỉ giáo viên mới được phép tạo phiên điểm danh
    if current_user.get('role') != 'teacher':
        return jsonify({"message": "Chỉ giáo viên mới được phép tạo phiên điểm danh"}), 403
    
    teacher_id = current_user.get('id')
    
    # Validate input
    required_fields = ['class_id', 'schedule_id', 'start_time', 'end_time']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Thiếu thông tin bắt buộc: {', '.join(missing_fields)}"}), 400
    
    # Kiểm tra lớp học và lịch học tồn tại
    class_ = Class.query.get(data['class_id'])
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404
    
    schedule = Schedule.query.get(data['schedule_id'])
    if not schedule:
        return jsonify({"message": "Lịch học không tồn tại"}), 404
    
    # Kiểm tra giáo viên có phụ trách lớp này không
    # (Có thể cần thêm logic kiểm tra)
    
    # Kiểm tra thời gian điểm danh nằm trong thời gian của lịch học
    try:
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        
        # Kiểm tra end_time phải sau start_time
        if end_time <= start_time:
            return jsonify({"message": "Thời gian kết thúc phải sau thời gian bắt đầu"}), 400
        
        # Kiểm tra thời gian điểm danh không được vượt quá thời gian của schedule
        schedule_start = datetime.combine(
            datetime.now().date(), 
            schedule.start_time
        )
        schedule_end = datetime.combine(
            datetime.now().date(), 
            schedule.end_time
        )
        
        if start_time.time() < schedule.start_time or end_time.time() > schedule.end_time:
            return jsonify({
                "message": "Thời gian điểm danh phải nằm trong khoảng thời gian của lịch học"
            }), 400
    except ValueError:
        return jsonify({"message": "Định dạng thời gian không hợp lệ"}), 400
    
    # Lấy danh sách sinh viên trong lớp
    class_students = ClassStudent.query.filter_by(class_id=data['class_id']).all()
    if not class_students:
        return jsonify({"message": "Lớp học không có sinh viên nào"}), 400
    
    # Lưu IP của giáo viên để kiểm tra khi sinh viên điểm danh
    # Sử dụng IP public từ frontend nếu có
    teacher_ip = data.get('public_ip', '127.0.0.1')
    
    # Tạo các bản ghi điểm danh cho từng sinh viên với trạng thái mặc định là ABSENT
    attendance_records = []
    for class_student in class_students:
        attendance = Attendance(
            student_id=class_student.student_id,
            class_id=data['class_id'],
            schedule_id=data['schedule_id'],
            start_time=start_time,
            end_time=end_time,
            status='ABSENT',  # Mặc định là vắng mặt
            recorded_by=teacher_id,
            notes=data.get('notes', ''),
            ip_public=teacher_ip  # Lưu IP public vào trường riêng
        )
        db.session.add(attendance)
        attendance_records.append(attendance)
    
    db.session.flush()  # Để có ID cho các bản ghi
    
    # Lưu thông tin phiên điểm danh để sử dụng sau này
    db.session.commit()
    
    return jsonify({
        "message": "Đã tạo phiên điểm danh thành công",
        "attendance_session": {
            "class_id": data['class_id'],
            "schedule_id": data['schedule_id'],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "teacher_ip": teacher_ip,
            "student_count": len(class_students),
            "records": [{"id": a.id, "student_id": a.student_id} for a in attendance_records]
        }
    }), 201

@attendance_bp.route('/student/attendance-sessions', methods=['GET'])
@auth_required
def get_student_attendance_sessions():
    """
    API để sinh viên lấy danh sách các phiên điểm danh có thể tham gia
    """
    current_user = get_current_user()
    
    # Chỉ sinh viên mới được phép sử dụng API này
    if current_user.get('role') != 'student':
        return jsonify({"message": "Chỉ sinh viên mới được phép sử dụng API này"}), 403
    
    student_id = current_user.get('id')
    now = datetime.now()
    
    # Lấy danh sách các lớp học mà sinh viên đang tham gia
    student_classes = ClassStudent.query.filter_by(student_id=student_id).all()
    class_ids = [sc.class_id for sc in student_classes]
    
    # Lấy danh sách các phiên điểm danh đang mở (chưa hết hạn)
    active_attendance_records = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.class_id.in_(class_ids),
        Attendance.end_time >= now,
        Attendance.status == 'ABSENT'  # Chỉ lấy những bản ghi chưa điểm danh
    ).all()
    
    # Gom nhóm theo class_id và schedule_id để hiển thị theo phiên
    attendance_sessions = {}
    for record in active_attendance_records:
        key = f"{record.class_id}_{record.schedule_id}"
        if key not in attendance_sessions:
            class_ = Class.query.get(record.class_id)
            schedule = Schedule.query.get(record.schedule_id)
            
            # Chuyển đổi mã ngày sang tên tiếng Việt
            day_names = {
                'MON': 'Thứ hai',
                'TUE': 'Thứ ba',
                'WED': 'Thứ tư',
                'THU': 'Thứ năm',
                'FRI': 'Thứ sáu',
                'SAT': 'Thứ bảy',
                'SUN': 'Chủ nhật'
            }
            
            attendance_sessions[key] = {
                "class_id": record.class_id,
                "class_name": class_.code if class_ else "Unknown",
                "schedule_id": record.schedule_id,
                "schedule_day": day_names.get(schedule.day_of_week, schedule.day_of_week) if schedule else "Unknown",
                "schedule_time": f"{schedule.start_time} - {schedule.end_time}" if schedule else "Unknown",
                "specific_date": schedule.specific_date.strftime('%d/%m/%Y') if schedule and schedule.specific_date else "Unknown",
                "attendance_id": record.id,
                "start_time": record.start_time,
                "end_time": record.end_time,
                "status": record.status
            }
    
    return jsonify({
        "attendance_sessions": list(attendance_sessions.values())
    })

@attendance_bp.route('/student/mark-attendance', methods=['POST'])
@auth_required
def mark_attendance():
    """
    API để sinh viên điểm danh bằng khuôn mặt
    
    Input: {
        "attendance_id": int,     # ID của bản ghi điểm danh
        "face_image": string,     # Ảnh khuôn mặt dạng base64
        "public_ip": string       # IP public của sinh viên (không bắt buộc)
    }
    """
    data = request.get_json()
    current_user = get_current_user()
    
    # Chỉ sinh viên mới được phép điểm danh
    if current_user.get('role') != 'student':
        return jsonify({"message": "Chỉ sinh viên mới được phép điểm danh"}), 403
    
    student_id = current_user.get('id')
    
    # Validate input
    if not data or 'attendance_id' not in data or 'face_image' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    # Lấy thông tin bản ghi điểm danh
    attendance = Attendance.query.get(data['attendance_id'])
    if not attendance:
        return jsonify({"message": "Không tìm thấy bản ghi điểm danh"}), 404
    
    # Kiểm tra bản ghi điểm danh có phải của sinh viên hiện tại không
    if attendance.student_id != student_id:
        return jsonify({"message": "Bản ghi điểm danh không thuộc về sinh viên này"}), 403
    
    # Kiểm tra phiên điểm danh còn hiệu lực không
    now = datetime.now()
    if now < attendance.start_time:
        return jsonify({"message": "Phiên điểm danh chưa bắt đầu"}), 400
    if now > attendance.end_time:
        return jsonify({"message": "Phiên điểm danh đã kết thúc"}), 400
    
    # Kiểm tra trạng thái điểm danh hiện tại
    if attendance.status != 'ABSENT':
        return jsonify({"message": f"Bạn đã điểm danh trước đó với trạng thái: {attendance.status}"}), 400
    
    # Lấy IP public của giáo viên từ trường ip_public
    teacher_ip = attendance.ip_public
    
    # Kiểm tra IP của sinh viên và giáo viên
    # Chỉ sử dụng IP public từ frontend
    student_ip = data.get('public_ip')
    if teacher_ip and student_ip:
        # Kiểm tra IP của sinh viên và giáo viên có giống nhau không
        if student_ip != teacher_ip:
            return jsonify({
                "message": "Địa chỉ IP của bạn không khớp với IP của giáo viên. Vui lòng đảm bảo bạn đang ở trong cùng một mạng."
            }), 403
    
    # Tìm thông tin sinh viên để lấy face_encoding
    student = Student.query.get(student_id)
    if not student or not student.face_encoding:
        return jsonify({"message": "Sinh viên chưa có dữ liệu khuôn mặt, vui lòng cập nhật"}), 400
    
    # Kiểm tra khuôn mặt
    face_encoding = encode_face_from_base64(data['face_image'])
    if not face_encoding:
        return jsonify({"message": "Không phát hiện khuôn mặt trong ảnh"}), 400
    
    if not check_face(face_encoding, student.face_encoding):
        return jsonify({"message": "Khuôn mặt không khớp với dữ liệu trong hệ thống"}), 403
    
    # Cập nhật trạng thái điểm danh
    attendance.status = 'PRESENT'
    attendance.notes = (attendance.notes or "") + f"\nĐiểm danh thành công lúc {now.strftime('%Y-%m-%d %H:%M:%S')}"
    db.session.commit()
    
    return jsonify({
        "message": "Điểm danh thành công",
        "attendance": {
            "id": attendance.id,
            "class_id": attendance.class_id,
            "status": attendance.status,
            "timestamp": now.isoformat()
        }
    })

@attendance_bp.route('/teacher/class-attendance/<int:class_id>', methods=['GET'])
@auth_required
def get_class_attendance(class_id):
    """
    API để giáo viên xem danh sách điểm danh của một lớp học
    """
    current_user = get_current_user()
    
    # Chỉ giáo viên mới được phép xem danh sách điểm danh của lớp
    if current_user.get('role') != 'teacher':
        return jsonify({"message": "Chỉ giáo viên mới được phép xem danh sách điểm danh của lớp"}), 403
    
    teacher_id = current_user.get('id')
    
    # Kiểm tra lớp học tồn tại
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404
    
    # Lấy danh sách các buổi điểm danh của lớp, nhóm theo schedule_id
    attendance_sessions = db.session.query(
        Attendance.schedule_id,
        Attendance.start_time,
        Attendance.end_time,
        db.func.count(Attendance.id).label('total_students'),
        db.func.sum(
            db.case(
                (Attendance.status == 'PRESENT', 1),
                else_=0
            )
        ).label('present_count'),
        db.func.sum(
            db.case(
                (Attendance.status == 'ABSENT', 1),
                else_=0
            )
        ).label('absent_count'),
        db.func.sum(
            db.case(
                (Attendance.status == 'EXCUSED', 1),
                else_=0
            )
        ).label('excused_count')
    ).filter(
        Attendance.class_id == class_id,
        Attendance.recorded_by == teacher_id
    ).group_by(
        Attendance.schedule_id,
        Attendance.start_time,
        Attendance.end_time
    ).all()
    
    result = []
    for session in attendance_sessions:
        schedule = Schedule.query.get(session.schedule_id)
        
        # Chuyển đổi mã ngày sang tên tiếng Việt
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
            "schedule_id": session.schedule_id,
            "day_of_week": day_names.get(schedule.day_of_week, schedule.day_of_week) if schedule else "Unknown",
            "schedule_time": f"{schedule.start_time} - {schedule.end_time}" if schedule else "Unknown",
            "specific_date": schedule.specific_date.strftime('%d/%m/%Y') if schedule and schedule.specific_date else "Unknown",
            "attendance_start": session.start_time.isoformat() if session.start_time else None,
            "attendance_end": session.end_time.isoformat() if session.end_time else None,
            "total_students": session.total_students,
            "present_count": session.present_count or 0,
            "absent_count": session.absent_count or 0,
            "excused_count": session.excused_count or 0,
            "attendance_rate": f"{((session.present_count or 0) / session.total_students * 100):.1f}%" if session.total_students > 0 else "0%"
        })
    
    return jsonify({
        "class_id": class_id,
        "class_code": class_.code,
        "attendance_sessions": result
    })

@attendance_bp.route('/teacher/attendance-details/<int:class_id>/<int:schedule_id>', methods=['GET'])
@auth_required
def get_attendance_details(class_id, schedule_id):
    """
    API để giáo viên xem chi tiết điểm danh của một buổi học cụ thể
    """
    current_user = get_current_user()
    
    # Chỉ giáo viên mới được phép xem chi tiết điểm danh
    if current_user.get('role') != 'teacher':
        return jsonify({"message": "Chỉ giáo viên mới được phép xem chi tiết điểm danh"}), 403
    
    # Lấy thông tin thời gian điểm danh từ query parameters
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    query = Attendance.query.filter(
        Attendance.class_id == class_id,
        Attendance.schedule_id == schedule_id
    )
    
    if start_time and end_time:
        try:
            start_datetime = datetime.fromisoformat(start_time)
            end_datetime = datetime.fromisoformat(end_time)
            query = query.filter(
                Attendance.start_time == start_datetime,
                Attendance.end_time == end_datetime
            )
        except ValueError:
            pass
    
    attendance_records = query.all()
    
    result = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        
        result.append({
            "attendance_id": record.id,
            "student_id": record.student_id,
            "student_name": f"{student.last_name} {student.first_name}" if student else "Unknown",
            "status": record.status,
            "notes": record.notes,
            "attendance_time": record.updated_at.isoformat() if record.updated_at else None
        })
    
    # Sắp xếp theo tên sinh viên
    result.sort(key=lambda x: x["student_name"])
    
    return jsonify({
        "class_id": class_id,
        "schedule_id": schedule_id,
        "attendance_records": result
    })

@attendance_bp.route('/teacher/update-attendance-status/<int:attendance_id>', methods=['PUT'])
@auth_required
def update_attendance_status(attendance_id):
    """
    API để giáo viên cập nhật trạng thái điểm danh của sinh viên
    
    Input: {
        "status": string,         # PRESENT, ABSENT, EXCUSED
        "notes": string           # Ghi chú (không bắt buộc)
    }
    """
    current_user = get_current_user()
    
    # Chỉ giáo viên mới được phép cập nhật trạng thái điểm danh
    if current_user.get('role') != 'teacher':
        return jsonify({"message": "Chỉ giáo viên mới được phép cập nhật trạng thái điểm danh"}), 403
    
    teacher_id = current_user.get('id')
    data = request.get_json()
    
    # Validate input
    if not data or 'status' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    if data['status'] not in ['PRESENT', 'ABSENT', 'EXCUSED']:
        return jsonify({"message": "Trạng thái không hợp lệ"}), 400
    
    # Lấy bản ghi điểm danh
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({"message": "Không tìm thấy bản ghi điểm danh"}), 404
    
    # Kiểm tra người cập nhật có phải là người tạo điểm danh không
    if attendance.recorded_by != teacher_id:
        return jsonify({"message": "Bạn không có quyền cập nhật bản ghi điểm danh này"}), 403
    
    # Cập nhật trạng thái
    old_status = attendance.status
    attendance.status = data['status']
    
    if 'notes' in data:
        attendance.notes = (attendance.notes or "") + f"\nCập nhật từ {old_status} thành {data['status']} bởi giáo viên {teacher_id} - {data.get('notes', '')}"
    
    db.session.commit()
    
    return jsonify({
        "message": "Cập nhật trạng thái điểm danh thành công",
        "attendance": {
            "id": attendance.id,
            "student_id": attendance.student_id,
            "status": attendance.status
        }
    })

@attendance_bp.route('/student/attendance-history', methods=['GET'])
@auth_required
def get_student_attendance_history():
    """
    API để sinh viên xem lịch sử điểm danh của mình
    """
    current_user = get_current_user()
    
    # Chỉ sinh viên mới được phép sử dụng API này
    if current_user.get('role') != 'student':
        return jsonify({"message": "Chỉ sinh viên mới được phép sử dụng API này"}), 403
    
    student_id = current_user.get('id')
    class_id = request.args.get('class_id')
    
    # Xây dựng query
    query = Attendance.query.filter(Attendance.student_id == student_id)
    
    # Nếu có filter theo lớp học
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    
    # Lấy tất cả bản ghi điểm danh
    attendance_records = query.order_by(Attendance.created_at.desc()).all()
    
    # Chuyển đổi mã ngày sang tên tiếng Việt
    day_names = {
        'MON': 'Thứ hai',
        'TUE': 'Thứ ba',
        'WED': 'Thứ tư',
        'THU': 'Thứ năm',
        'FRI': 'Thứ sáu',
        'SAT': 'Thứ bảy',
        'SUN': 'Chủ nhật'
    }
    
    result = []
    for record in attendance_records:
        class_ = Class.query.get(record.class_id)
        schedule = Schedule.query.get(record.schedule_id)
        
        result.append({
            "id": record.id,
            "class_id": record.class_id,
            "class_name": class_.code if class_ else "Unknown",
            "schedule_id": record.schedule_id,
            "schedule_day": day_names.get(schedule.day_of_week, schedule.day_of_week) if schedule else "Unknown",
            "schedule_time": f"{schedule.start_time} - {schedule.end_time}" if schedule else "Unknown",
            "specific_date": schedule.specific_date.strftime('%d/%m/%Y') if schedule and schedule.specific_date else "Unknown",
            "status": record.status,
            "attendance_time": record.updated_at.isoformat() if record.updated_at != record.created_at else None
        })
    
    return jsonify({
        "attendance_records": result
    })