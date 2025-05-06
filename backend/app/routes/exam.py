from flask import Blueprint, request, jsonify, g
from app import db
from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.models.question import Question
from app.models.answer import Answer
from app.models.classs import Class
from app.models.class_teacher import ClassTeacher
from app.utils.auth import auth_required, admin_required, teacher_or_admin_required
from datetime import datetime

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/exams', methods=['POST'])
@teacher_or_admin_required
def create_exam():
    """Tạo mới kỳ thi"""
    data = request.get_json()

    # Validate input
    required_fields = ['title', 'exam_date', 'duration_minutes', 'class_id', 
                     'exam_start_time', 'exam_end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Thiếu thông tin bắt buộc: {field}"}), 400

    # Check if class exists
    class_ = Class.query.get(data['class_id'])
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404

    # Kiểm tra quyền truy cập cho giáo viên
    if g.role == 'teacher':
        class_id = data.get('class_id')
        
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền thao tác với lớp học này"}), 403

    # Create new exam
    new_exam = Exam(
        title=data['title'],
        description=data.get('description'),
        exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date(),
        duration_minutes=data['duration_minutes'],
        class_id=data['class_id'],
        exam_start_time=datetime.strptime(data['exam_start_time'], '%H:%M').time(),
        exam_end_time=datetime.strptime(data['exam_end_time'], '%H:%M').time()
    )
    db.session.add(new_exam)
    db.session.commit()
    
    # Nếu có questions, thêm vào exam
    if 'questions' in data and isinstance(data['questions'], list):
        for question_data in data['questions']:
            if 'question_id' in question_data and 'points' in question_data:
                # Kiểm tra xem question có tồn tại không
                question = Question.query.get(question_data['question_id'])
                if not question:
                    continue
                
                # Thêm question vào exam
                exam_question = ExamQuestion(
                    exam_id=new_exam.id,
                    question_id=question_data['question_id'],
                    points=question_data['points']
                )
                db.session.add(exam_question)
        
        db.session.commit()
    
    return jsonify({"message": "Exam created successfully", "id": new_exam.id}), 201

@exam_bp.route('/exams', methods=['GET'])
@auth_required
def get_exams():
    """Lấy danh sách tất cả kỳ thi"""
    # Nếu là giáo viên, chỉ lấy kỳ thi của các lớp đang dạy
    if g.role == 'teacher':
        # Lấy danh sách lớp học mà giáo viên dạy
        classes_taught = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        classes_taught = [cls[0] for cls in classes_taught]
        
        if not classes_taught:
            return jsonify([])
        
        exams = Exam.query.filter(Exam.class_id.in_(classes_taught)).all()
    # Nếu là student, chỉ lấy kỳ thi của các lớp mình học
    elif g.role == 'student':
        from app.models.class_student import ClassStudent
        
        # Lấy danh sách lớp học mà học sinh học
        classes_studied = db.session.query(ClassStudent.class_id).filter_by(student_id=g.student_id).all()
        classes_studied = [cls[0] for cls in classes_studied]
        
        if not classes_studied:
            return jsonify([])
        
        exams = Exam.query.filter(Exam.class_id.in_(classes_studied)).all()
    # Nếu là admin, lấy tất cả
    else:
        exams = Exam.query.all()
    
    return jsonify([{
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "exam_date": exam.exam_date.strftime('%Y-%m-%d'),
        "duration_minutes": exam.duration_minutes,
        "class_id": exam.class_id,
        "exam_start_time": exam.exam_start_time.strftime('%H:%M'),
        "exam_end_time": exam.exam_end_time.strftime('%H:%M'),
        "created_at": exam.created_at,
        "updated_at": exam.updated_at
    } for exam in exams])

@exam_bp.route('/exams/<int:id>', methods=['GET'])
@auth_required
def get_exam(id):
    """Lấy thông tin chi tiết của một kỳ thi"""
    exam = Exam.query.get_or_404(id)
    
    # Kiểm tra quyền truy cập
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem kỳ thi này"}), 403
    elif g.role == 'student':
        # Kiểm tra xem học sinh có học lớp này không
        from app.models.class_student import ClassStudent
        student_class = ClassStudent.query.filter_by(
            student_id=g.student_id,
            class_id=exam.class_id
        ).first()
        
        if not student_class:
            return jsonify({"message": "Bạn không có quyền xem kỳ thi này"}), 403
    
    # Lấy tất cả câu hỏi của kỳ thi
    exam_questions = ExamQuestion.query.filter_by(exam_id=id).all()
    questions = []
    
    for eq in exam_questions:
        question = Question.query.get(eq.question_id)
        if question:
            question_data = {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "points": eq.points,
                "answers": []
            }
            
            # Thêm các đáp án nếu không phải là câu hỏi tự luận
            if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                answers = Answer.query.filter_by(question_id=question.id).all()
                question_data["answers"] = [{
                    "id": answer.id,
                    "answer_text": answer.answer_text,
                    "is_correct": answer.is_correct if g.role != 'student' else None  # Ẩn đáp án đúng với học sinh
                } for answer in answers]
            
            questions.append(question_data)
    
    return jsonify({
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "exam_date": exam.exam_date.strftime('%Y-%m-%d'),
        "duration_minutes": exam.duration_minutes,
        "class_id": exam.class_id,
        "exam_start_time": exam.exam_start_time.strftime('%H:%M'),
        "exam_end_time": exam.exam_end_time.strftime('%H:%M'),
        "created_at": exam.created_at,
        "updated_at": exam.updated_at,
        "questions": questions
    })

@exam_bp.route('/exams/<int:id>', methods=['PUT'])
@teacher_or_admin_required
def update_exam(id):
    """Cập nhật thông tin kỳ thi"""
    data = request.get_json()
    exam = Exam.query.get_or_404(id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của kỳ thi này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền cập nhật kỳ thi của lớp học này"}), 403

    # Cập nhật các thông tin kỳ thi
    if 'title' in data:
        exam.title = data['title']
    if 'description' in data:
        exam.description = data['description']
    if 'exam_date' in data:
        exam.exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date()
    if 'duration_minutes' in data:
        exam.duration_minutes = data['duration_minutes']
    if 'exam_start_time' in data:
        exam.exam_start_time = datetime.strptime(data['exam_start_time'], '%H:%M').time()
    if 'exam_end_time' in data:
        exam.exam_end_time = datetime.strptime(data['exam_end_time'], '%H:%M').time()

    # Cập nhật danh sách câu hỏi nếu có
    if 'questions' in data:
        # Xóa tất cả các câu hỏi hiện tại
        ExamQuestion.query.filter_by(exam_id=id).delete()
        
        # Thêm danh sách câu hỏi mới
        for question_data in data['questions']:
            if 'question_id' in question_data and 'points' in question_data:
                # Kiểm tra xem question có tồn tại không
                question = Question.query.get(question_data['question_id'])
                if not question:
                    continue
                
                # Thêm question vào exam
                exam_question = ExamQuestion(
                    exam_id=exam.id,
                    question_id=question_data['question_id'],
                    points=question_data['points']
                )
                db.session.add(exam_question)

    db.session.commit()
    return jsonify({"message": "Exam updated successfully"})

@exam_bp.route('/exams/<int:id>', methods=['DELETE'])
@teacher_or_admin_required
def delete_exam(id):
    """Xóa một kỳ thi"""
    exam = Exam.query.get_or_404(id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của kỳ thi này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xóa kỳ thi của lớp học này"}), 403
    
    # Xóa tất cả các câu hỏi của kỳ thi
    ExamQuestion.query.filter_by(exam_id=id).delete()
    
    # Xóa kỳ thi
    db.session.delete(exam)
    db.session.commit()
    return jsonify({"message": "Exam deleted successfully"})

@exam_bp.route('/classes/<int:class_id>/exams', methods=['GET'])
@auth_required
def get_exams_by_class(class_id):
    """Lấy danh sách kỳ thi theo lớp học"""
    # Kiểm tra quyền
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem kỳ thi của lớp học này"}), 403
    elif g.role == 'student':
        # Kiểm tra xem học sinh có học lớp này không
        from app.models.class_student import ClassStudent
        student_class = ClassStudent.query.filter_by(
            student_id=g.student_id,
            class_id=class_id
        ).first()
        
        if not student_class:
            return jsonify({"message": "Bạn không có quyền xem kỳ thi của lớp học này"}), 403
    
    # Lấy kỳ thi theo lớp
    exams = Exam.query.filter_by(class_id=class_id).all()
    
    return jsonify([{
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "exam_date": exam.exam_date.strftime('%Y-%m-%d'),
        "duration_minutes": exam.duration_minutes,
        "class_id": exam.class_id,
        "exam_start_time": exam.exam_start_time.strftime('%H:%M'),
        "exam_end_time": exam.exam_end_time.strftime('%H:%M'),
        "created_at": exam.created_at,
        "updated_at": exam.updated_at
    } for exam in exams])

@exam_bp.route('/exams/<int:exam_id>/questions', methods=['GET'])
@auth_required
def get_exam_questions(exam_id):
    """Lấy danh sách câu hỏi của kỳ thi"""
    exam = Exam.query.get_or_404(exam_id)
    
    # Kiểm tra quyền truy cập
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem câu hỏi của kỳ thi này"}), 403
    elif g.role == 'student':
        # Kiểm tra xem học sinh có học lớp này không
        from app.models.class_student import ClassStudent
        student_class = ClassStudent.query.filter_by(
            student_id=g.student_id,
            class_id=exam.class_id
        ).first()
        
        if not student_class:
            return jsonify({"message": "Bạn không có quyền xem câu hỏi của kỳ thi này"}), 403
    
    # Lấy tất cả câu hỏi của kỳ thi
    exam_questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
    questions = []
    
    for eq in exam_questions:
        question = Question.query.get(eq.question_id)
        if question:
            question_data = {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "points": eq.points,
                "answers": []
            }
            
            # Thêm các đáp án nếu không phải là câu hỏi tự luận
            if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                answers = Answer.query.filter_by(question_id=question.id).all()
                question_data["answers"] = [{
                    "id": answer.id,
                    "answer_text": answer.answer_text,
                    "is_correct": answer.is_correct if g.role != 'student' else None  # Ẩn đáp án đúng với học sinh
                } for answer in answers]
            
            questions.append(question_data)
    
    return jsonify(questions)

@exam_bp.route('/exams/<int:exam_id>/questions', methods=['POST'])
@teacher_or_admin_required
def add_question_to_exam(exam_id):
    """Thêm câu hỏi vào kỳ thi"""
    data = request.get_json()
    exam = Exam.query.get_or_404(exam_id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của kỳ thi này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền thêm câu hỏi vào kỳ thi của lớp học này"}), 403
    
    # Validate input
    if not data or 'question_id' not in data or 'points' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    # Kiểm tra xem question có tồn tại không
    question = Question.query.get(data['question_id'])
    if not question:
        return jsonify({"message": "Câu hỏi không tồn tại"}), 404
    
    # Kiểm tra xem question đã được thêm vào exam chưa
    existing_question = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_id=data['question_id']
    ).first()
    
    if existing_question:
        return jsonify({"message": "Câu hỏi đã được thêm vào kỳ thi"}), 400
    
    # Thêm question vào exam
    exam_question = ExamQuestion(
        exam_id=exam_id,
        question_id=data['question_id'],
        points=data['points']
    )
    db.session.add(exam_question)
    db.session.commit()
    
    return jsonify({"message": "Câu hỏi đã được thêm vào kỳ thi", "id": exam_question.id}), 201

@exam_bp.route('/exams/<int:exam_id>/questions/<int:question_id>', methods=['DELETE'])
@teacher_or_admin_required
def remove_question_from_exam(exam_id, question_id):
    """Xóa câu hỏi khỏi kỳ thi"""
    exam = Exam.query.get_or_404(exam_id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của kỳ thi này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xóa câu hỏi khỏi kỳ thi của lớp học này"}), 403
    
    # Tìm và xóa exam_question
    exam_question = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_id=question_id
    ).first_or_404()
    
    db.session.delete(exam_question)
    db.session.commit()
    
    return jsonify({"message": "Câu hỏi đã được xóa khỏi kỳ thi"})

@exam_bp.route('/exams/<int:exam_id>/questions/<int:question_id>', methods=['PUT'])
@teacher_or_admin_required
def update_exam_question(exam_id, question_id):
    """Cập nhật thông tin câu hỏi trong kỳ thi (điểm số)"""
    data = request.get_json()
    exam = Exam.query.get_or_404(exam_id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của kỳ thi này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=exam.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền cập nhật câu hỏi trong kỳ thi của lớp học này"}), 403
    
    # Tìm exam_question
    exam_question = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_id=question_id
    ).first_or_404()
    
    # Cập nhật điểm
    if 'points' in data:
        exam_question.points = data['points']
    
    db.session.commit()
    
    return jsonify({"message": "Cập nhật thành công"}) 