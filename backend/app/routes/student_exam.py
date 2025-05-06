from flask import Blueprint, jsonify, request, g
from app import db
from app.models.exam import Exam
from app.models.classs import Class
from app.models.class_student import ClassStudent
from app.models.question import Question
from app.models.exam_question import ExamQuestion
from app.models.answer import Answer
from app.models.student_exam_answer import StudentExamAnswer
from app.utils.auth import student_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import logging

student_exam_bp = Blueprint('student_exam', __name__)

@student_exam_bp.route('/student/exams', methods=['GET'])
@student_required
def get_student_exams():
    """
    Get all exams for a student based on their enrolled classes.
    """
    try:
        student_id = g.student_id
        logging.info(f"Fetching exams for student ID: {student_id}")
        
        # Get current datetime
        now = datetime.now()
        
        # Find all classes the student is enrolled in
        enrolled_classes = db.session.query(ClassStudent.class_id).\
            filter(ClassStudent.student_id == student_id).all()
        
        enrolled_class_ids = [c[0] for c in enrolled_classes]
        
        if not enrolled_class_ids:
            logging.info(f"No enrolled classes found for student {student_id}")
            return jsonify({
                'success': True,
                'message': 'No enrolled classes found',
                'exams': []
            }), 200
            
        # Find all exams for those classes
        exams = db.session.query(Exam, Class).\
            join(Class, Exam.class_id == Class.id).\
            filter(Exam.class_id.in_(enrolled_class_ids)).\
            order_by(Exam.exam_date.desc()).all()
            
        result = []
        
        for exam, class_obj in exams:
            # Calculate exam status based on current time and exam date/times
            exam_date = exam.exam_date
            exam_start_time = exam.exam_start_time
            exam_end_time = exam.exam_end_time
            
            # Combine date and time for comparison
            now_date = now.date()
            now_time = now.time()
            
            if now_date < exam_date or (now_date == exam_date and now_time < exam_start_time):
                status = 'upcoming'
                status_code = 'yellow'
            elif now_date > exam_date or (now_date == exam_date and now_time > exam_end_time):
                status = 'expired'
                status_code = 'red'
            else:
                status = 'active'
                status_code = 'green'
                
            # Check if the student has already answered this exam
            has_answered = db.session.query(StudentExamAnswer).\
                filter(StudentExamAnswer.student_id == student_id, 
                       StudentExamAnswer.exam_id == exam.id).first() is not None
                
            # Count total questions
            question_count = db.session.query(ExamQuestion).\
                filter(ExamQuestion.exam_id == exam.id).count()
                
            # Calculate total points
            total_points_query = db.session.query(db.func.sum(ExamQuestion.points)).\
                filter(ExamQuestion.exam_id == exam.id).scalar()
            total_points = total_points_query or 0
                
            exam_data = {
                'id': exam.id,
                'title': exam.title,
                'description': exam.description,
                'exam_date': exam.exam_date.strftime('%Y-%m-%d'),
                'duration_minutes': exam.duration_minutes,
                'start_time': exam.exam_start_time.strftime('%H:%M'),
                'end_time': exam.exam_end_time.strftime('%H:%M'),
                'total_points': total_points,
                'status': status,
                'status_code': status_code,
                'class_id': class_obj.id,
                'class_code': class_obj.code,
                'question_count': question_count,
                'has_answered': has_answered
            }
            result.append(exam_data)
            
        return jsonify({
            'success': True,
            'message': 'Student exams retrieved successfully',
            'exams': result
        }), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    except Exception as e:
        logging.error(f"Error getting student exams: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving student exams',
            'error': str(e)
        }), 500

@student_exam_bp.route('/student/exams/<int:exam_id>', methods=['GET'])
@student_required
def get_student_exam_detail(exam_id):
    """
    Get details of a specific exam for a student, including questions
    """
    try:
        student_id = g.student_id
        
        # Check if the exam exists
        exam = db.session.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404
            
        # Check if the student is enrolled in the class
        is_enrolled = db.session.query(ClassStudent).\
            filter(ClassStudent.student_id == student_id, 
                   ClassStudent.class_id == exam.class_id).first()
                   
        if not is_enrolled:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this class'
            }), 403
            
        # Get class info
        class_obj = db.session.query(Class).filter(Class.id == exam.class_id).first()
        
        # Get current datetime
        now = datetime.now()
        now_date = now.date()
        now_time = now.time()
        
        # Calculate exam status
        if now_date < exam.exam_date or (now_date == exam.exam_date and now_time < exam.exam_start_time):
            status = 'upcoming'
            status_code = 'yellow'
            # Don't show questions for upcoming exams
            return jsonify({
                'success': False,
                'message': 'This exam has not started yet',
                'exam': {
                    'id': exam.id,
                    'title': exam.title,
                    'description': exam.description,
                    'exam_date': exam.exam_date.strftime('%Y-%m-%d'),
                    'duration_minutes': exam.duration_minutes,
                    'start_time': exam.exam_start_time.strftime('%H:%M'),
                    'end_time': exam.exam_end_time.strftime('%H:%M'),
                    'status': status,
                    'status_code': status_code,
                    'class_id': class_obj.id,
                    'class_code': class_obj.code
                }
            }), 403
        elif now_date > exam.exam_date or (now_date == exam.exam_date and now_time > exam.exam_end_time):
            status = 'expired'
            status_code = 'red'
        else:
            status = 'active'
            status_code = 'green'
            
        # Get exam questions through ExamQuestion
        exam_questions = db.session.query(ExamQuestion, Question).\
            join(Question, ExamQuestion.question_id == Question.id).\
            filter(ExamQuestion.exam_id == exam_id).\
            order_by(ExamQuestion.id).all()
            
        # Check if student has already answered
        student_answers = db.session.query(StudentExamAnswer).\
            filter(StudentExamAnswer.student_id == student_id, 
                   StudentExamAnswer.exam_id == exam_id).all()
                   
        student_answers_dict = {answer.question_id: answer for answer in student_answers}
        
        # Calculate total points
        total_points = sum(eq.points for eq, _ in exam_questions)
        
        question_list = []
        for exam_question, question in exam_questions:
            student_answer = student_answers_dict.get(question.id)
            
            # Get answer options for multiple choice questions
            answer_options = []
            if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                answers = db.session.query(Answer).\
                    filter(Answer.question_id == question.id).all()
                answer_options = [{
                    'id': answer.id,
                    'text': answer.answer_text,
                    # Only show correct answers if exam is expired
                    'is_correct': answer.is_correct if status == 'expired' else None
                } for answer in answers]
            
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'points': exam_question.points,
                'answers': answer_options,
                'student_answer': student_answer.answer_text if student_answer else None,
                'is_correct': student_answer.is_correct if student_answer and status == 'expired' else None,
                'score': student_answer.score if student_answer and status == 'expired' else None
            }
            question_list.append(question_data)
            
        # Calculate total score if exam is expired
        total_score = None
        if status == 'expired' and student_answers:
            total_score = sum(answer.score or 0 for answer in student_answers)
            
        result = {
            'id': exam.id,
            'title': exam.title,
            'description': exam.description,
            'exam_date': exam.exam_date.strftime('%Y-%m-%d'),
            'duration_minutes': exam.duration_minutes,
            'start_time': exam.exam_start_time.strftime('%H:%M'),
            'end_time': exam.exam_end_time.strftime('%H:%M'),
            'total_points': total_points,
            'status': status,
            'status_code': status_code,
            'class_id': class_obj.id,
            'class_code': class_obj.code,
            'questions': question_list,
            'total_score': total_score
        }
        
        return jsonify({
            'success': True,
            'message': 'Exam details retrieved successfully',
            'exam': result
        }), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    except Exception as e:
        logging.error(f"Error getting exam details: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving exam details',
            'error': str(e)
        }), 500

@student_exam_bp.route('/student/exams/<int:exam_id>/submit', methods=['POST'])
@student_required
def submit_exam_answers(exam_id):
    """
    Submit answers for an exam
    """
    try:
        student_id = g.student_id
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'Invalid request data'
            }), 400
            
        answers = data['answers']
        
        # Check if exam exists
        exam = db.session.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404
            
        # Check if student is enrolled in the class
        is_enrolled = db.session.query(ClassStudent).\
            filter(ClassStudent.student_id == student_id, 
                   ClassStudent.class_id == exam.class_id).first()
                   
        if not is_enrolled:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this class'
            }), 403
            
        # Check if exam is active
        now = datetime.now()
        now_date = now.date()
        now_time = now.time()
        
        if now_date < exam.exam_date or (now_date == exam.exam_date and now_time < exam.exam_start_time):
            return jsonify({
                'success': False,
                'message': 'This exam has not started yet'
            }), 403
            
        if now_date > exam.exam_date or (now_date == exam.exam_date and now_time > exam.exam_end_time):
            return jsonify({
                'success': False,
                'message': 'This exam has ended'
            }), 403
            
        # Get exam questions through ExamQuestion
        exam_questions = db.session.query(ExamQuestion, Question).\
            join(Question, ExamQuestion.question_id == Question.id).\
            filter(ExamQuestion.exam_id == exam_id).all()
            
        exam_question_dict = {q.id: (eq, q) for eq, q in exam_questions}
        
        # Process and save answers
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer_text')
            
            if not question_id or question_id not in exam_question_dict:
                continue
                
            exam_question, question = exam_question_dict[question_id]
            
            # Check if an answer already exists for this question
            existing_answer = db.session.query(StudentExamAnswer).\
                filter(StudentExamAnswer.student_id == student_id,
                       StudentExamAnswer.exam_id == exam_id,
                       StudentExamAnswer.question_id == question_id).first()
                       
            # Calculate is_correct for multiple choice questions
            is_correct = None
            score = None
            
            if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                # Get correct answer
                correct_answer = db.session.query(Answer).\
                    filter(Answer.question_id == question_id, 
                           Answer.is_correct == True).first()
                
                if correct_answer and str(correct_answer.id) == str(answer_text):
                    is_correct = True
                    score = exam_question.points
                else:
                    is_correct = False
                    score = 0
                
            if existing_answer:
                # Update existing answer
                existing_answer.answer_text = answer_text
                existing_answer.is_correct = is_correct
                existing_answer.score = score
                existing_answer.updated_at = datetime.utcnow()
            else:
                # Create new answer
                new_answer = StudentExamAnswer(
                    student_id=student_id,
                    exam_id=exam_id,
                    question_id=question_id,
                    answer_text=answer_text,
                    is_correct=is_correct,
                    score=score
                )
                db.session.add(new_answer)
                
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Exam answers submitted successfully'
        }), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500
    except Exception as e:
        logging.error(f"Error submitting exam answers: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting exam answers',
            'error': str(e)
        }), 500 