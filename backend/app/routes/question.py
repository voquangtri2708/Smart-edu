from flask import Blueprint, request, jsonify, g
from app import db
from app.models.question import Question
from app.models.answer import Answer
from app.utils.auth import auth_required, admin_required, teacher_or_admin_required
from datetime import datetime

question_bp = Blueprint('question', __name__)

@question_bp.route('/questions', methods=['POST'])
@teacher_or_admin_required
def create_question():
    """Tạo mới câu hỏi"""
    data = request.get_json()

    # Validate input
    if not data or 'question_text' not in data or 'question_type' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

    # Kiểm tra loại câu hỏi hợp lệ
    valid_types = ['MULTIPLE_CHOICE', 'TRUE_FALSE', 'ESSAY', 'SHORT_ANSWER']
    if data['question_type'] not in valid_types:
        return jsonify({"message": f"Loại câu hỏi không hợp lệ. Phải là một trong: {', '.join(valid_types)}"}), 400

    # Tạo câu hỏi mới
    new_question = Question(
        question_text=data['question_text'],
        question_type=data['question_type']
    )
    db.session.add(new_question)
    db.session.commit()
    
    # Xử lý thêm các đáp án nếu là câu hỏi trắc nghiệm
    if data['question_type'] in ['MULTIPLE_CHOICE', 'TRUE_FALSE'] and 'answers' in data:
        for answer_data in data['answers']:
            if 'answer_text' in answer_data:
                new_answer = Answer(
                    question_id=new_question.id,
                    answer_text=answer_data['answer_text'],
                    is_correct=answer_data.get('is_correct', False)
                )
                db.session.add(new_answer)
        
        db.session.commit()
    
    response = {
        "message": "Câu hỏi đã được tạo thành công",
        "id": new_question.id
    }
    
    # Thêm thông tin đáp án cho response
    if data['question_type'] in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
        answers = Answer.query.filter_by(question_id=new_question.id).all()
        response["answers"] = [{
            "id": answer.id,
            "answer_text": answer.answer_text,
            "is_correct": answer.is_correct
        } for answer in answers]
    
    return jsonify(response), 201

@question_bp.route('/questions', methods=['GET'])
@auth_required
def get_questions():
    """Lấy danh sách tất cả câu hỏi"""
    # Lọc theo loại câu hỏi nếu có
    question_type = request.args.get('type')
    
    query = Question.query
    if question_type:
        query = query.filter_by(question_type=question_type)
    
    # Phân trang nếu cần
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page)
    questions = pagination.items
    
    result = []
    for question in questions:
        question_data = {
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "created_at": question.created_at,
            "updated_at": question.updated_at
        }
        
        # Thêm đáp án nếu là câu hỏi trắc nghiệm
        if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
            answers = Answer.query.filter_by(question_id=question.id).all()
            question_data["answers"] = [{
                "id": answer.id,
                "answer_text": answer.answer_text,
                "is_correct": answer.is_correct
            } for answer in answers]
        
        result.append(question_data)
    
    return jsonify({
        "questions": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    })

@question_bp.route('/questions/<int:id>', methods=['GET'])
@auth_required
def get_question(id):
    """Lấy thông tin chi tiết của một câu hỏi"""
    question = Question.query.get_or_404(id)
    
    question_data = {
        "id": question.id,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "created_at": question.created_at,
        "updated_at": question.updated_at
    }
    
    # Thêm đáp án nếu là câu hỏi trắc nghiệm
    if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
        answers = Answer.query.filter_by(question_id=question.id).all()
        question_data["answers"] = [{
            "id": answer.id,
            "answer_text": answer.answer_text,
            "is_correct": answer.is_correct
        } for answer in answers]
    
    return jsonify(question_data)

@question_bp.route('/questions/<int:id>', methods=['PUT'])
@teacher_or_admin_required
def update_question(id):
    """Cập nhật thông tin câu hỏi"""
    data = request.get_json()
    question = Question.query.get_or_404(id)

    # Cập nhật thông tin câu hỏi
    if 'question_text' in data:
        question.question_text = data['question_text']
    
    # Thường không cho phép thay đổi loại câu hỏi vì sẽ ảnh hưởng đến đáp án
    # nhưng có thể mở nếu cần
    if 'question_type' in data and question.question_type != data['question_type']:
        # Kiểm tra loại câu hỏi hợp lệ
        valid_types = ['MULTIPLE_CHOICE', 'TRUE_FALSE', 'ESSAY', 'SHORT_ANSWER']
        if data['question_type'] not in valid_types:
            return jsonify({"message": f"Loại câu hỏi không hợp lệ. Phải là một trong: {', '.join(valid_types)}"}), 400
        
        # Nếu chuyển từ trắc nghiệm sang tự luận, xóa tất cả đáp án
        if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE'] and data['question_type'] in ['ESSAY', 'SHORT_ANSWER']:
            Answer.query.filter_by(question_id=id).delete()
        
        question.question_type = data['question_type']

    # Cập nhật đáp án nếu là câu hỏi trắc nghiệm
    if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE'] and 'answers' in data:
        # Xóa tất cả đáp án hiện tại
        Answer.query.filter_by(question_id=id).delete()
        
        # Thêm đáp án mới
        for answer_data in data['answers']:
            if 'answer_text' in answer_data:
                new_answer = Answer(
                    question_id=id,
                    answer_text=answer_data['answer_text'],
                    is_correct=answer_data.get('is_correct', False)
                )
                db.session.add(new_answer)

    db.session.commit()
    
    # Chuẩn bị response
    response = {"message": "Câu hỏi đã được cập nhật thành công"}
    
    # Thêm thông tin đáp án cho response nếu là câu hỏi trắc nghiệm
    if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
        answers = Answer.query.filter_by(question_id=id).all()
        response["answers"] = [{
            "id": answer.id,
            "answer_text": answer.answer_text,
            "is_correct": answer.is_correct
        } for answer in answers]
    
    return jsonify(response)

@question_bp.route('/questions/<int:id>', methods=['DELETE'])
@teacher_or_admin_required
def delete_question(id):
    """Xóa một câu hỏi"""
    question = Question.query.get_or_404(id)
    
    # Xóa tất cả đáp án liên quan
    Answer.query.filter_by(question_id=id).delete()
    
    # Xóa câu hỏi trong các kỳ thi
    from app.models.exam_question import ExamQuestion
    ExamQuestion.query.filter_by(question_id=id).delete()
    
    # Xóa câu hỏi
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({"message": "Câu hỏi đã được xóa thành công"})

@question_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
@teacher_or_admin_required
def add_answer(question_id):
    """Thêm đáp án cho câu hỏi"""
    data = request.get_json()
    question = Question.query.get_or_404(question_id)
    
    # Kiểm tra loại câu hỏi
    if question.question_type not in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
        return jsonify({"message": "Chỉ có thể thêm đáp án cho câu hỏi trắc nghiệm"}), 400
    
    # Validate input
    if not data or 'answer_text' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400
    
    # Tạo đáp án mới
    new_answer = Answer(
        question_id=question_id,
        answer_text=data['answer_text'],
        is_correct=data.get('is_correct', False)
    )
    db.session.add(new_answer)
    db.session.commit()
    
    return jsonify({
        "message": "Đáp án đã được thêm thành công",
        "id": new_answer.id,
        "answer_text": new_answer.answer_text,
        "is_correct": new_answer.is_correct
    }), 201

@question_bp.route('/questions/<int:question_id>/answers/<int:answer_id>', methods=['PUT'])
@teacher_or_admin_required
def update_answer(question_id, answer_id):
    """Cập nhật đáp án"""
    data = request.get_json()
    answer = Answer.query.filter_by(id=answer_id, question_id=question_id).first_or_404()
    
    if 'answer_text' in data:
        answer.answer_text = data['answer_text']
    if 'is_correct' in data:
        answer.is_correct = data['is_correct']
    
    db.session.commit()
    
    return jsonify({
        "message": "Đáp án đã được cập nhật thành công",
        "id": answer.id,
        "answer_text": answer.answer_text,
        "is_correct": answer.is_correct
    })

@question_bp.route('/questions/<int:question_id>/answers/<int:answer_id>', methods=['DELETE'])
@teacher_or_admin_required
def delete_answer(question_id, answer_id):
    """Xóa đáp án"""
    answer = Answer.query.filter_by(id=answer_id, question_id=question_id).first_or_404()
    
    db.session.delete(answer)
    db.session.commit()
    
    return jsonify({"message": "Đáp án đã được xóa thành công"})

@question_bp.route('/search/questions', methods=['GET'])
@auth_required
def search_questions():
    """Tìm kiếm câu hỏi theo text"""
    keyword = request.args.get('q', '')
    question_type = request.args.get('type')
    
    if not keyword:
        return jsonify({"message": "Cần nhập từ khóa tìm kiếm"}), 400
    
    # Tìm kiếm câu hỏi theo từ khóa
    query = Question.query.filter(Question.question_text.like(f'%{keyword}%'))
    
    # Lọc theo loại câu hỏi nếu có
    if question_type:
        query = query.filter_by(question_type=question_type)
    
    # Phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page)
    questions = pagination.items
    
    result = []
    for question in questions:
        question_data = {
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "created_at": question.created_at,
            "updated_at": question.updated_at
        }
        
        # Thêm đáp án nếu là câu hỏi trắc nghiệm
        if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
            answers = Answer.query.filter_by(question_id=question.id).all()
            question_data["answers"] = [{
                "id": answer.id,
                "answer_text": answer.answer_text,
                "is_correct": answer.is_correct
            } for answer in answers]
        
        result.append(question_data)
    
    return jsonify({
        "questions": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }) 