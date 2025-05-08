from flask import Blueprint, request, jsonify, g
from app import db
from app.models.grade import Grade
from app.models.student import Student
from app.models.classs import Class
from app.models.grade_type import GradeType
from app.models.exam import Exam
from app.models.class_teacher import ClassTeacher
from app.utils.auth import auth_required, admin_required, teacher_or_admin_required

grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/grades', methods=['POST'])
@teacher_or_admin_required
def create_grade():
    """Tạo mới một điểm số"""
    data = request.get_json()

    # Validate input
    if not data or 'student_id' not in data or 'class_id' not in data or 'grade_type_id' not in data or 'score' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        class_id = data.get('class_id')
        
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền thao tác với lớp học này"}), 403

    # Check if student, class, grade type, and exam exist
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({"message": "Học sinh không tồn tại"}), 404

    class_ = Class.query.get(data['class_id'])
    if not class_:
        return jsonify({"message": "Lớp học không tồn tại"}), 404

    grade_type = GradeType.query.get(data['grade_type_id'])
    if not grade_type:
        return jsonify({"message": "Loại điểm không tồn tại"}), 404

    # Kiểm tra exam nếu có
    exam_id = data.get('exam_id')
    if exam_id:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({"message": "Kỳ thi không tồn tại"}), 404

    # Create new grade
    new_grade = Grade(
        student_id=data['student_id'],
        class_id=data['class_id'],
        grade_type_id=data['grade_type_id'],
        exam_id=data.get('exam_id'),
        score=data['score']
    )
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"message": "Grade created successfully", "id": new_grade.id}), 201

@grade_bp.route('/grades', methods=['GET'])
@auth_required
def get_grades():
    """Lấy danh sách tất cả điểm số"""
    # Nếu là giáo viên, chỉ lấy điểm của các lớp đang dạy
    if g.role == 'teacher':
        # Lấy danh sách lớp học mà giáo viên dạy
        classes_taught = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        classes_taught = [cls[0] for cls in classes_taught]
        
        if not classes_taught:
            return jsonify([])
        
        grades = Grade.query.filter(Grade.class_id.in_(classes_taught)).all()
    # Nếu là student, chỉ lấy điểm của mình
    elif g.role == 'student':
        grades = Grade.query.filter_by(student_id=g.student_id).all()
    # Nếu là admin, lấy tất cả
    else:
        grades = Grade.query.all()
    
    return jsonify([{
        "id": grade.id,
        "student_id": grade.student_id,
        "class_id": grade.class_id,
        "grade_type_id": grade.grade_type_id,
        "exam_id": grade.exam_id,
        "score": grade.score,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at
    } for grade in grades])

@grade_bp.route('/grades/<int:id>', methods=['GET'])
@auth_required
def get_grade(id):
    """Lấy thông tin chi tiết của một điểm số"""
    grade = Grade.query.get_or_404(id)
    
    # Kiểm tra quyền truy cập
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=grade.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem điểm này"}), 403
    elif g.role == 'student' and g.student_id != grade.student_id:
        return jsonify({"message": "Bạn không có quyền xem điểm này"}), 403
    
    return jsonify({
        "id": grade.id,
        "student_id": grade.student_id,
        "class_id": grade.class_id,
        "grade_type_id": grade.grade_type_id,
        "exam_id": grade.exam_id,
        "score": grade.score,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at
    })

@grade_bp.route('/grades/<int:id>', methods=['PUT'])
@teacher_or_admin_required
def update_grade(id):
    """Cập nhật thông tin điểm số"""
    data = request.get_json()
    grade = Grade.query.get_or_404(id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của điểm này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=grade.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền cập nhật điểm của lớp học này"}), 403

    if 'score' in data:
        grade.score = data['score']
    if 'exam_id' in data:
        exam = Exam.query.get(data['exam_id'])
        if not exam:
            return jsonify({"message": "Kỳ thi không tồn tại"}), 404
        grade.exam_id = data['exam_id']

    db.session.commit()
    return jsonify({"message": "Grade updated successfully"})

@grade_bp.route('/grades/<int:id>', methods=['DELETE'])
@teacher_or_admin_required
def delete_grade(id):
    """Xóa một điểm số"""
    grade = Grade.query.get_or_404(id)
    
    # Kiểm tra quyền cho giáo viên
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp của điểm này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=grade.class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xóa điểm của lớp học này"}), 403
            
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"message": "Grade deleted successfully"})

@grade_bp.route('/classes/<int:class_id>/grades', methods=['GET'])
@auth_required
def get_grades_by_class(class_id):
    """Lấy danh sách điểm số theo lớp học"""
    # Kiểm tra quyền
    if g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem điểm của lớp học này"}), 403
    elif g.role == 'student':
        # Học sinh chỉ được xem điểm của lớp mình học
        from app.models.class_student import ClassStudent
        student_class = ClassStudent.query.filter_by(
            student_id=g.student_id,
            class_id=class_id
        ).first()
        
        if not student_class:
            return jsonify({"message": "Bạn không có quyền xem điểm của lớp học này"}), 403
    
    # Lấy điểm theo lớp
    grades = Grade.query.filter_by(class_id=class_id).all()
    
    return jsonify([{
        "id": grade.id,
        "student_id": grade.student_id,
        "class_id": grade.class_id,
        "grade_type_id": grade.grade_type_id,
        "exam_id": grade.exam_id,
        "score": grade.score,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at
    } for grade in grades])

@grade_bp.route('/students/<string:student_id>/grades', methods=['GET'])
@auth_required
def get_grades_by_student(student_id):
    """Lấy danh sách điểm số theo học sinh"""
    # Kiểm tra quyền
    if g.role == 'student' and g.student_id != student_id:
        return jsonify({"message": "Bạn không có quyền xem điểm của học sinh khác"}), 403
    elif g.role == 'teacher':
        # Giáo viên chỉ được xem điểm của học sinh trong lớp mình dạy
        # Lấy danh sách lớp học mà giáo viên dạy
        classes_taught = db.session.query(ClassTeacher.class_id).filter_by(teacher_id=g.teacher_id).all()
        classes_taught = [cls[0] for cls in classes_taught]
        
        # Kiểm tra xem học sinh có trong các lớp giáo viên dạy không
        from app.models.class_student import ClassStudent
        student_in_classes = ClassStudent.query.filter(
            ClassStudent.student_id == student_id,
            ClassStudent.class_id.in_(classes_taught)
        ).first()
        
        if not student_in_classes:
            return jsonify({"message": "Bạn không có quyền xem điểm của học sinh này"}), 403
    
    # Lấy điểm theo học sinh
    grades = Grade.query.filter_by(student_id=student_id).all()
    
    return jsonify([{
        "id": grade.id,
        "student_id": grade.student_id,
        "class_id": grade.class_id,
        "grade_type_id": grade.grade_type_id,
        "exam_id": grade.exam_id,
        "score": grade.score,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at
    } for grade in grades])

@grade_bp.route('/classes/<int:class_id>/students/<string:student_id>/grades', methods=['GET'])
@auth_required
def get_grades_by_class_and_student(class_id, student_id):
    """Lấy danh sách điểm số theo lớp học và học sinh"""
    # Kiểm tra quyền
    if g.role == 'student' and g.student_id != student_id:
        return jsonify({"message": "Bạn không có quyền xem điểm của học sinh khác"}), 403
    elif g.role == 'teacher':
        # Kiểm tra xem giáo viên có dạy lớp này không
        teacher_class = ClassTeacher.query.filter_by(
            teacher_id=g.teacher_id,
            class_id=class_id
        ).first()
        
        if not teacher_class:
            return jsonify({"message": "Bạn không có quyền xem điểm của lớp học này"}), 403
    
    # Lấy điểm theo lớp và học sinh
    grades = Grade.query.filter_by(class_id=class_id, student_id=student_id).all()
    
    return jsonify([{
        "id": grade.id,
        "student_id": grade.student_id,
        "class_id": grade.class_id,
        "grade_type_id": grade.grade_type_id,
        "exam_id": grade.exam_id,
        "score": grade.score,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at
    } for grade in grades])