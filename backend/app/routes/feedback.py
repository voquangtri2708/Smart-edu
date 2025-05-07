from flask import Blueprint, request, jsonify, g
from app import db
from app.models.feedback import Feedback
from app.models.classs import Class
from app.models.class_student import ClassStudent
from app.models.class_teacher import ClassTeacher
from app.models.subject import Subject
from app.ml.pred import prediction
from app.utils.auth import auth_required, admin_required, student_self_or_admin_required
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import logging
from app.models.classroom import Classroom
from app.models.building import Building
from app.models.campus import Campus
from app.models.teacher import Teacher
import json
import requests
import os

feedback_bp = Blueprint('feedback', __name__)

# Thêm endpoint xử lý preflight OPTIONS request
@feedback_bp.route('/feedbacks', methods=['OPTIONS'])
def handle_feedbacks_options():
    resp = jsonify({'success': True})
    # Thêm CORS headers
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Max-Age'] = '3600'
    return resp, 200

@feedback_bp.route('/feedbacks', methods=['POST'])
@auth_required
def create_feedback():
    try:
        data = request.get_json()
        logging.info(f"Received feedback data: {data}")
        
        # Chỉ học sinh mới có thể tạo đánh giá
        logging.info(f"Current user role: {g.role}, student_id: {g.student_id}")
        if g.role != 'student':
            return jsonify({"message": "Chỉ học sinh mới có quyền đánh giá"}), 403
        
        student_id = g.student_id  # Lấy student_id từ token
        class_id = data.get('class_id')
        feedback_type = data.get('feedback_type')
        teacher_id = data.get('teacher_id')
        classroom_id = data.get('classroom_id')
        content = data.get('content')
        
        logging.info(f"Processing feedback - student_id: {student_id}, class_id: {class_id}, feedback_type: {feedback_type}")
        
        # Validation
        if not all([student_id, class_id, feedback_type, content]):
            logging.warning(f"Missing required information: student_id={student_id}, class_id={class_id}, feedback_type={feedback_type}, content={'present' if content else 'missing'}")
            return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
        
        if feedback_type not in ['TEACHER', 'CLASSROOM']:
            logging.warning(f"Invalid feedback type: {feedback_type}")
            return jsonify({"message": "Loại đánh giá không hợp lệ"}), 400
        
        if feedback_type == 'TEACHER' and not teacher_id:
            logging.warning("Missing teacher_id for TEACHER feedback")
            return jsonify({"message": "Thiếu thông tin giảng viên"}), 400
        
        if feedback_type == 'CLASSROOM' and not classroom_id:
            logging.warning("Missing classroom_id for CLASSROOM feedback")
            return jsonify({"message": "Thiếu thông tin phòng học"}), 400
        
        # Kiểm tra học sinh có thuộc lớp không
        student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
        logging.info(f"Student in class check: {student_in_class}")
        if not student_in_class:
            logging.warning(f"Student {student_id} not found in class {class_id}")
            return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
        
        # Kiểm tra giảng viên có dạy lớp không (nếu là đánh giá giảng viên)
        if feedback_type == 'TEACHER':
            teacher_in_class = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
            logging.info(f"Teacher in class check: {teacher_in_class}")
            if not teacher_in_class:
                logging.warning(f"Teacher {teacher_id} not found in class {class_id}")
                return jsonify({"message": "Giảng viên không dạy lớp này"}), 403
        
        # Kiểm tra học sinh đã đánh giá trong lớp này chưa
        if feedback_type == 'TEACHER':
            existing_feedback = Feedback.query.filter_by(
                student_id=student_id,
                class_id=class_id,
                teacher_id=teacher_id,
                feedback_type='TEACHER'
            ).first()
            
            if existing_feedback:
                logging.info(f"Student {student_id} already gave feedback to teacher {teacher_id} in class {class_id}")
                return jsonify({"message": "Bạn đã đánh giá giảng viên này trong lớp này"}), 409
        else:
            existing_feedback = Feedback.query.filter_by(
                student_id=student_id,
                class_id=class_id,
                classroom_id=classroom_id,
                feedback_type='CLASSROOM'
            ).first()
            
            if existing_feedback:
                logging.info(f"Student {student_id} already gave feedback to classroom {classroom_id} in class {class_id}")
                return jsonify({"message": "Bạn đã đánh giá phòng học này trong lớp này"}), 409
        
        # Lấy start_date và end_date từ bảng class và tính end_date + 7 ngày
        class_ = Class.query.get_or_404(class_id)
        start_date = class_.start_date
        end_date = class_.end_date
        
        # Kiểm tra thời gian có nằm trong khoảng cho phép đánh giá không
        current_date = datetime.now().date()
        feedback_end_date = end_date + timedelta(days=7)
        
        logging.info(f"Date check - current: {current_date}, start: {start_date}, end: {feedback_end_date}")
        if current_date < start_date:
            logging.warning(f"Too early to give feedback - current: {current_date}, start: {start_date}")
            return jsonify({"message": "Chưa đến thời gian đánh giá"}), 403
        if current_date > feedback_end_date:
            logging.warning(f"Too late to give feedback - current: {current_date}, end: {feedback_end_date}")
            return jsonify({"message": "Đã kết thúc thời gian đánh giá"}), 403
        
        # Dự đoán sentiment sử dụng model
        try:
            probs, sentiment_label = prediction(content)
            if sentiment_label is None:
                # Nếu không nhận dạng được từ nào trong từ điển
                logging.warning(f"Input text has no words in vocabulary: {content}")
                predicted_sentiment = "NEUTRAL"  # Mặc định là trung lập
            else:
                sentiment_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
                predicted_sentiment = sentiment_map[sentiment_label]
                logging.info(f"Sentiment prediction: {predicted_sentiment}, probabilities: {probs}")
        except Exception as e:
            logging.error(f"Sentiment prediction error: {str(e)}")
            predicted_sentiment = "NEUTRAL"  # Default if prediction fails
        
        new_feedback = Feedback(
            content=content,
            student_id=student_id,
            class_id=class_id,
            teacher_id=teacher_id if feedback_type == 'TEACHER' else None,
            classroom_id=classroom_id if feedback_type == 'CLASSROOM' else None,
            start_date=start_date,
            end_date=feedback_end_date,
            sentiment=predicted_sentiment,
            feedback_type=feedback_type
        )
        
        try:
            db.session.add(new_feedback)
            db.session.commit()
            logging.info(f"Feedback created successfully - id: {new_feedback.id}")
            return jsonify({"message": "Feedback created successfully"}), 201
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"IntegrityError: {str(e)}")
            return jsonify({"message": f"Lỗi: {str(e)}"}), 400
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating feedback: {str(e)}")
            return jsonify({"message": f"Lỗi không xác định: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unhandled exception in create_feedback: {str(e)}")
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@feedback_bp.route('/feedbacks', methods=['GET'])
@auth_required
def get_feedbacks():
    """Lấy danh sách đánh giá có thể lọc theo các tham số"""
    feedback_type = request.args.get('feedback_type')
    sentiment = request.args.get('sentiment')
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    classroom_id = request.args.get('classroom_id')
    
    # Add date range parameters for updated_at field
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Xây dựng truy vấn với các bộ lọc
    query = Feedback.query
    
    # Nếu là admin: có thể xem tất cả feedback
    # Nếu là học sinh: chỉ xem được feedback của mình
    if g.role != 'admin':
        if g.role == 'student':
            query = query.filter_by(student_id=g.student_id)
        elif g.role == 'teacher':
            # Giảng viên chỉ xem được feedback về mình
            query = query.filter_by(teacher_id=g.teacher_id, feedback_type='TEACHER')
        else:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Áp dụng các bộ lọc
    if feedback_type:
        query = query.filter_by(feedback_type=feedback_type)
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    if student_id and g.role == 'admin':  # Chỉ admin mới có thể lọc theo student_id
        query = query.filter_by(student_id=student_id)
    if class_id:
        query = query.filter_by(class_id=class_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
    
    # Apply date range filter for updated_at field
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Feedback.updated_at >= start_datetime)
        except ValueError:
            return jsonify({"message": "Định dạng start_date không hợp lệ. Sử dụng YYYY-MM-DD"}), 400

    if end_date:
        try:
            # Set end_date to end of day (23:59:59)
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(Feedback.updated_at <= end_datetime)
        except ValueError:
            return jsonify({"message": "Định dạng end_date không hợp lệ. Sử dụng YYYY-MM-DD"}), 400
    
    # Apply search if provided
    search_query = request.args.get('query')
    if search_query:
        search_term = f"%{search_query}%"
        query = query.join(Teacher, Feedback.teacher_id == Teacher.id, isouter=True).filter(
            db.or_(
                Feedback.content.ilike(search_term),
                Feedback.student_id.ilike(search_term),
                db.and_(
                    Feedback.feedback_type == 'TEACHER',
                    db.or_(
                        Teacher.id.ilike(search_term),
                        db.func.concat(Teacher.last_name, ' ', Teacher.first_name).ilike(search_term)
                    )
                )
            )
        )
    
    # Sắp xếp từ mới đến cũ
    query = query.order_by(Feedback.created_at.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    feedbacks = pagination.items
    
    result = []
    for feedback in feedbacks:
        # Lấy thông tin về lớp học
        class_info = {}
        if feedback.class_id:
            class_ = Class.query.get(feedback.class_id)
            if class_:
                class_info = {
                    "class_code": class_.code,
                    "subject_name": None
                }
                # Lấy thông tin về môn học nếu có
                if class_.subject_id:
                    subject = Subject.query.get(class_.subject_id)
                    if subject:
                        class_info["subject_name"] = subject.name

        # Lấy thông tin về phòng học
        classroom_info = {}
        if feedback.classroom_id:
            classroom = Classroom.query.get(feedback.classroom_id)
            if classroom:
                classroom_info = {
                    "room_number": classroom.room_number,
                    "building_name": None,
                    "campus_name": None
                }
                # Lấy tên tòa nhà
                if classroom.building_id:
                    building = Building.query.get(classroom.building_id)
                    if building:
                        classroom_info["building_name"] = building.name
                        # Lấy tên cơ sở
                        if building.campus_id:
                            campus = Campus.query.get(building.campus_id)
                            if campus:
                                classroom_info["campus_name"] = campus.name

        # Lấy thông tin giảng viên
        teacher_info = {}
        if feedback.teacher_id:
            teacher = Teacher.query.get(feedback.teacher_id)
            if teacher:
                teacher_info = {
                    "id": teacher.id,
                    "name": teacher.last_name + " " + teacher.first_name
                }


        
        result.append({
            "id": feedback.id,
            "content": feedback.content,
            "student_id": feedback.student_id,
            "class_id": feedback.class_id,
            "class_info": class_info,
            "classroom_info": classroom_info,
            "teacher_id": feedback.teacher_id,
            "teacher_info": teacher_info,
            "classroom_id": feedback.classroom_id,
            "start_date": feedback.start_date.strftime('%Y-%m-%d') if feedback.start_date else None,
            "end_date": feedback.end_date.strftime('%Y-%m-%d') if feedback.end_date else None,
            "sentiment": feedback.sentiment,
            "feedback_type": feedback.feedback_type,
            "created_at": feedback.created_at
        })
    
    return jsonify({
        'items': result,
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@feedback_bp.route('/feedbacks/<int:id>', methods=['GET'])
@auth_required
def get_feedback(id):
    """Lấy thông tin chi tiết của một đánh giá"""
    feedback = Feedback.query.get_or_404(id)
    
    # Kiểm tra quyền: admin xem được tất cả, học sinh chỉ xem được feedback của mình
    if g.role != 'admin':
        if g.role == 'student' and feedback.student_id != g.student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
        elif g.role == 'teacher' and (feedback.teacher_id != g.teacher_id or feedback.feedback_type != 'TEACHER'):
            return jsonify({"message": "Không có quyền truy cập"}), 403
        elif g.role not in ['student', 'teacher', 'admin']:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Lấy thông tin về lớp học
    class_info = {}
    if feedback.class_id:
        class_ = Class.query.get(feedback.class_id)
        if class_:
            class_info = {
                "class_code": class_.code,
                "subject_name": None
            }
            # Lấy thông tin về môn học nếu có
            if class_.subject_id:
                subject = Subject.query.get(class_.subject_id)
                if subject:
                    class_info["subject_name"] = subject.name

    # Lấy thông tin về phòng học
    classroom_info = {}
    if feedback.classroom_id:
        classroom = Classroom.query.get(feedback.classroom_id)
        if classroom:
            classroom_info = {
                "room_number": classroom.room_number,
                "building_name": None,
                "campus_name": None
            }
            # Lấy tên tòa nhà
            if classroom.building_id:
                building = Building.query.get(classroom.building_id)
                if building:
                    classroom_info["building_name"] = building.name
                    # Lấy tên cơ sở
                    if building.campus_id:
                        campus = Campus.query.get(building.campus_id)
                        if campus:
                            classroom_info["campus_name"] = campus.name

    # Lấy thông tin giảng viên
    teacher_info = {}
    if feedback.teacher_id:
        teacher = Teacher.query.get(feedback.teacher_id)
        if teacher:
            teacher_info = {
                "id": teacher.id,
                "name": teacher.last_name + " " + teacher.first_name
            }
    
    
    return jsonify({
        "id": feedback.id,
        "content": feedback.content,
        "student_id": feedback.student_id,
        "class_id": feedback.class_id,
        "class_info": class_info,
        "classroom_info": classroom_info,
        "teacher_id": feedback.teacher_id,
        "teacher_info": teacher_info,
        "classroom_id": feedback.classroom_id,
        "start_date": feedback.start_date.strftime('%Y-%m-%d') if feedback.start_date else None,
        "end_date": feedback.end_date.strftime('%Y-%m-%d') if feedback.end_date else None,
        "sentiment": feedback.sentiment,
        "feedback_type": feedback.feedback_type,
        "created_at": feedback.created_at
    })

@feedback_bp.route('/feedbacks/<int:id>', methods=['DELETE'])
@auth_required
def delete_feedback(id):
    """Xóa một đánh giá"""
    feedback = Feedback.query.get_or_404(id)
    
    # Chỉ admin mới có thể xóa feedback, hoặc học sinh xóa feedback của chính mình
    if g.role != 'admin':
        if g.role != 'student' or feedback.student_id != g.student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
        
        # Học sinh chỉ có thể xóa feedback trong khoảng thời gian nhất định (ví dụ: 24 giờ sau khi tạo)
        current_time = datetime.now()
        feedback_time = feedback.created_at
        time_diff = current_time - feedback_time
        
        if time_diff.total_seconds() > 24 * 60 * 60:  # 24 giờ
            return jsonify({"message": "Không thể xóa đánh giá sau 24 giờ"}), 403
    
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback deleted successfully"})

@feedback_bp.route('/feedbacks/student/<string:student_id>/classes/<int:class_id>/teachers', methods=['GET'])
@auth_required
def get_teachers_for_feedback(student_id, class_id):
    """Lấy danh sách giảng viên mà học sinh có thể đánh giá"""
    logging.info(f"Getting teachers for student {student_id} in class {class_id}")
    
    # Kiểm tra quyền: chỉ admin hoặc chính học sinh đó mới có thể xem
    if g.role != 'admin':
        if g.role != 'student' or g.student_id != student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    # Kiểm tra học sinh có thuộc lớp không
    try:
        student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
        logging.info(f"Student in class check: {student_in_class}")
        
        if not student_in_class:
            logging.warning(f"Student {student_id} not found in class {class_id}")
            return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
        
        # Lấy danh sách giảng viên đã được đánh giá bởi học sinh này trong lớp này
        evaluated_teachers = db.session.query(Feedback.teacher_id).filter_by(
            student_id=student_id,
            class_id=class_id,
            feedback_type='TEACHER'
        ).all()
        
        evaluated_teacher_ids = [t.teacher_id for t in evaluated_teachers]
        logging.info(f"Evaluated teacher IDs: {evaluated_teacher_ids}")
        
        # Lấy tất cả giảng viên trong lớp học
        class_teachers = ClassTeacher.query.filter_by(class_id=class_id).all()
        logging.info(f"Class teachers count: {len(class_teachers)}")
        
        # Lọc ra các giảng viên chưa được đánh giá
        available_teachers = []
        
        for class_teacher in class_teachers:
            teacher = class_teacher.teacher
            if teacher.id not in evaluated_teacher_ids:
                available_teachers.append({
                    "id": teacher.id,
                    "first_name": teacher.first_name,
                    "last_name": teacher.last_name,
                    "email": teacher.email
                })
        
        logging.info(f"Available teachers count: {len(available_teachers)}")
        return jsonify(available_teachers)
    except Exception as e:
        logging.error(f"Error in get_teachers_for_feedback: {str(e)}")
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@feedback_bp.route('/feedbacks/student/<string:student_id>/classes/<int:class_id>/classrooms', methods=['GET'])
@auth_required
def get_classrooms_for_feedback(student_id, class_id):
    """Lấy danh sách phòng học mà học sinh có thể đánh giá"""
    logging.info(f"Getting classrooms for student {student_id} in class {class_id}")
    
    # Kiểm tra quyền: chỉ admin hoặc chính học sinh đó mới có thể xem
    if g.role != 'admin':
        if g.role != 'student' or g.student_id != student_id:
            return jsonify({"message": "Không có quyền truy cập"}), 403
    
    try:
        # Kiểm tra học sinh có thuộc lớp không
        student_in_class = ClassStudent.query.filter_by(student_id=student_id, class_id=class_id).first()
        logging.info(f"Student in class check: {student_in_class}")
        
        if not student_in_class:
            logging.warning(f"Student {student_id} not found in class {class_id}")
            return jsonify({"message": "Học sinh không thuộc lớp này"}), 403
        
        # Lấy danh sách phòng học đã được đánh giá bởi học sinh này trong lớp này
        evaluated_classrooms = db.session.query(Feedback.classroom_id).filter_by(
            student_id=student_id,
            class_id=class_id,
            feedback_type='CLASSROOM'
        ).all()
        
        evaluated_classroom_ids = [c.classroom_id for c in evaluated_classrooms]
        logging.info(f"Evaluated classroom IDs: {evaluated_classroom_ids}")
        
        # Lấy các phòng học từ lịch học của lớp này thay vì tất cả phòng học
        from app.models.schedule import Schedule
        from app.models.classroom import Classroom
        
        # Lấy các phòng học duy nhất từ lịch học của lớp
        classroom_ids_query = db.session.query(Schedule.classroom_id).filter(
            Schedule.class_id == class_id
        ).distinct()
        
        classroom_ids = [item[0] for item in classroom_ids_query.all()]
        logging.info(f"Found {len(classroom_ids)} classrooms in schedule for class {class_id}")
        
        # Lấy thông tin các phòng học từ bảng Classroom
        classrooms = Classroom.query.filter(Classroom.id.in_(classroom_ids)).all()
        logging.info(f"Total classrooms from schedule: {len(classrooms)}")
        
        # Lọc ra các phòng học chưa được đánh giá
        available_classrooms = []
        
        for classroom in classrooms:
            if classroom.id not in evaluated_classroom_ids:
                available_classrooms.append({
                    "id": classroom.id,
                    "room_number": classroom.room_number,
                    "capacity": classroom.capacity,
                    "building_id": classroom.building_id
                })
        
        logging.info(f"Available classrooms count: {len(available_classrooms)}")
        return jsonify(available_classrooms)
    except Exception as e:
        logging.error(f"Error in get_classrooms_for_feedback: {str(e)}")
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@feedback_bp.route('/feedbacks/generate-report', methods=['POST'])
@admin_required
def generate_feedback_report():
    """Tạo báo cáo phản hồi dựa trên khoảng thời gian"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({"message": "Thiếu thông tin ngày bắt đầu hoặc ngày kết thúc"}), 400
        
        # Format date for report title
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            report_period = f"từ ngày {start_date_obj.strftime('%d/%m/%Y')} đến ngày {end_date_obj.strftime('%d/%m/%Y')}"
        except ValueError:
            return jsonify({"message": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"}), 400
        
        # Fetch feedbacks for the specified date range
        feedbacks = get_feedbacks_for_report(start_date, end_date)
        
        if not feedbacks:
            return jsonify({"message": "Không có dữ liệu phản hồi trong khoảng thời gian đã chọn"}), 404
        
        # Format data for the prompt
        formatted_data = json.dumps(feedbacks, ensure_ascii=False)
        
        # Get the report prompt from prompt.txt
        with open('backend/app/templates/report_prompt.txt', 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        
        prompt = prompt_template.replace("{thời gian báo cáo: ví dụ \"tháng 4 năm 2025\", \"ngày 01/05/2025\", hoặc \"quý I năm 2025\"}", report_period)
        
        # Call Gemini API
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({"message": "Thiếu Gemini API key trong cấu hình"}), 500
        
        gemini_response = call_gemini_api(prompt, formatted_data, api_key)
        
        if not gemini_response:
            return jsonify({"message": "Không thể tạo báo cáo từ Gemini API"}), 500
        
        return jsonify({
            "report": gemini_response,
            "period": report_period,
            "feedback_count": len(feedbacks)
        })
    
    except Exception as e:
        logging.error(f"Error generating feedback report: {str(e)}")
        return jsonify({"message": f"Lỗi tạo báo cáo: {str(e)}"}), 500

def get_feedbacks_for_report(start_date, end_date):
    """Lấy danh sách đánh giá trong khoảng thời gian"""
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        
        # Query feedbacks in the date range
        feedbacks = Feedback.query.filter(
            Feedback.created_at >= start_datetime,
            Feedback.created_at <= end_datetime
        ).all()
        
        result = []
        for feedback in feedbacks:
            # Get class info
            class_info = {}
            if feedback.class_id:
                class_ = Class.query.get(feedback.class_id)
                if class_:
                    class_info = {
                        "class_code": class_.code,
                        "subject_name": None
                    }
                    # Get subject info
                    if class_.subject_id:
                        subject = Subject.query.get(class_.subject_id)
                        if subject:
                            class_info["subject_name"] = subject.name
            
            # Get classroom info
            classroom_info = {}
            if feedback.classroom_id:
                classroom = Classroom.query.get(feedback.classroom_id)
                if classroom:
                    classroom_info = {
                        "room_number": classroom.room_number,
                        "building_name": None,
                        "campus_name": None
                    }
                    # Get building name
                    if classroom.building_id:
                        building = Building.query.get(classroom.building_id)
                        if building:
                            classroom_info["building_name"] = building.name
                            # Get campus name
                            if building.campus_id:
                                campus = Campus.query.get(building.campus_id)
                                if campus:
                                    classroom_info["campus_name"] = campus.name
            
            # Get teacher info
            teacher_info = {}
            if feedback.teacher_id:
                teacher = Teacher.query.get(feedback.teacher_id)
                if teacher:
                    teacher_info = {
                        "id": teacher.id,
                        "name": teacher.last_name + " " + teacher.first_name
                    }
            
            result.append({
                "id": feedback.id,
                "content": feedback.content,
                "sentiment": feedback.sentiment,
                "class_info": class_info,
                "teacher_info": teacher_info,
                "classroom_info": classroom_info,
                "feedback_type": feedback.feedback_type,
                "created_at": feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    
    except Exception as e:
        logging.error(f"Error fetching feedbacks for report: {str(e)}")
        return []

def call_gemini_api(prompt, data, api_key):
    """Call the Gemini API to generate a report"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nDữ liệu phản hồi:\n\n```json\n{data}\n```"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.8,
                "maxOutputTokens": 8192
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            # Extract the generated text from the response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']
        
        logging.error(f"Gemini API error: {response.status_code} - {response.text}")
        return None
    
    except Exception as e:
        logging.error(f"Error calling Gemini API: {str(e)}")
        return None