from flask import Blueprint, request, jsonify
from app import db
from app.models.grade import Grade
from app.models.student import Student
from app.models.classs import Class
from app.models.grade_type import GradeType
# from app.models.exam import Exam
from app.utils.auth import auth_required, admin_required

grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/grades', methods=['POST'])
@admin_required
def create_grade():
    """Tạo mới một điểm số"""
    data = request.get_json()

    # Validate input
    if not data or 'student_id' not in data or 'class_id' not in data or 'grade_type_id' not in data or 'score' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

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

    exam = Exam.query.get(data.get('exam_id')) if 'exam_id' in data else None
    if 'exam_id' in data and not exam:
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
    return jsonify({"message": "Grade created successfully"}), 201

@grade_bp.route('/grades', methods=['GET'])
@auth_required
def get_grades():
    """Lấy danh sách tất cả điểm số"""
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
@admin_required
def update_grade(id):
    """Cập nhật thông tin điểm số"""
    data = request.get_json()
    grade = Grade.query.get_or_404(id)

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
@admin_required
def delete_grade(id):
    """Xóa một điểm số"""
    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"message": "Grade deleted successfully"})