from flask import Blueprint, jsonify, request, g
from app import db
from app.models.exam import Exam
from app.models.question import Question
from app.models.student import Student
from app.models.student_exam_answer import StudentExamAnswer
from app.models.exam_question import ExamQuestion
from app.models.answer import Answer
from app.utils.auth import teacher_required
from sqlalchemy.exc import SQLAlchemyError
import logging

student_exam_answer_bp = Blueprint('student_exam_answer', __name__)

@student_exam_answer_bp.route('/teacher/exams/<int:exam_id>/answers', methods=['GET'])
@teacher_required
def get_student_answers_for_exam(exam_id):
    """
    Get all student answers for a specific exam, grouped by student.
    Teachers can use this to review and grade student answers.
    """
    try:
        teacher_id = g.teacher_id
        
        # Check if exam exists
        exam = db.session.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404
            
        # Check if the teacher is authorized to view this exam (teaches the class)
        from app.models.class_teacher import ClassTeacher
        is_teacher = db.session.query(ClassTeacher).\
            filter(ClassTeacher.teacher_id == teacher_id, 
                   ClassTeacher.class_id == exam.class_id).first()
                   
        if not is_teacher:
            return jsonify({
                'success': False,
                'message': 'You are not authorized to view answers for this exam'
            }), 403
            
        # Get all questions for this exam using the join table
        exam_questions = db.session.query(Question, ExamQuestion).\
            join(ExamQuestion, Question.id == ExamQuestion.question_id).\
            filter(ExamQuestion.exam_id == exam_id).\
            all()
            
        # Get all student answers for this exam
        answers = db.session.query(
            StudentExamAnswer, Student
        ).join(
            Student, StudentExamAnswer.student_id == Student.id
        ).filter(
            StudentExamAnswer.exam_id == exam_id
        ).all()
        
        # Group answers by student
        student_answers = {}
        for answer, student in answers:
            student_id = student.id
            if student_id not in student_answers:
                student_answers[student_id] = {
                    'student_id': student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'student_code': student.id,
                    'answers': [],
                    'total_score': 0
                }
                
            # Add answer to student's answers
            student_answers[student_id]['answers'].append({
                'id': answer.id,
                'question_id': answer.question_id,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'score': answer.score
            })
            
            # Update total score if answer has been graded
            if answer.score is not None:
                student_answers[student_id]['total_score'] += answer.score
        
        # Convert dictionary to list
        result = list(student_answers.values())
        
        # Sort by student name
        result.sort(key=lambda x: x['student_name'])
        
        # Prepare question data with correct answers
        question_data = []
        for question, exam_question in exam_questions:
            # Get correct answers for multiple choice or true/false questions
            correct_answers = []
            if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                correct_answers = db.session.query(Answer).\
                    filter(Answer.question_id == question.id, Answer.is_correct == True).\
                    all()
            
            question_data.append({
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'points': exam_question.points,
                'correct_answers': [
                    {'id': answer.id, 'text': answer.answer_text}
                    for answer in correct_answers
                ] if correct_answers else []
            })
        
        return jsonify({
            'success': True,
            'message': 'Student answers retrieved successfully',
            'exam': {
                'id': exam.id,
                'title': exam.title,
                'description': exam.description
            },
            'questions': question_data,
            'student_answers': result
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
        logging.error(f"Error getting student answers: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving student answers',
            'error': str(e)
        }), 500

@student_exam_answer_bp.route('/teacher/exams/answers/<int:answer_id>', methods=['PUT'])
@teacher_required
def grade_student_answer(answer_id):
    """
    Grade a student's answer for a specific question.
    This is primarily for essay questions or questions that require manual grading.
    """
    try:
        teacher_id = g.teacher_id
        data = request.get_json()
        
        if not data or 'score' not in data:
            return jsonify({
                'success': False,
                'message': 'Score is required'
            }), 400
            
        score = data['score']
        
        # Validate score is a number
        try:
            score = float(score)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Score must be a number'
            }), 400
            
        # Get the answer
        student_answer = db.session.query(StudentExamAnswer).filter(
            StudentExamAnswer.id == answer_id
        ).first()
        
        if not student_answer:
            return jsonify({
                'success': False,
                'message': 'Answer not found'
            }), 404
            
        # Get the exam
        exam = db.session.query(Exam).filter(
            Exam.id == student_answer.exam_id
        ).first()
        
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404
            
        # Check if the teacher is authorized to grade this exam
        from app.models.class_teacher import ClassTeacher
        is_teacher = db.session.query(ClassTeacher).\
            filter(ClassTeacher.teacher_id == teacher_id, 
                   ClassTeacher.class_id == exam.class_id).first()
                   
        if not is_teacher:
            return jsonify({
                'success': False,
                'message': 'You are not authorized to grade answers for this exam'
            }), 403
            
        # Get the question to check max score
        question = db.session.query(Question).filter(
            Question.id == student_answer.question_id
        ).first()
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
            
        # Get the exam question to find the points value
        exam_question = db.session.query(ExamQuestion).filter(
            ExamQuestion.exam_id == student_answer.exam_id,
            ExamQuestion.question_id == student_answer.question_id
        ).first()
        
        if not exam_question:
            return jsonify({
                'success': False,
                'message': 'Exam question not found'
            }), 404
            
        # Validate score is not greater than question point value
        if score > exam_question.points:
            return jsonify({
                'success': False,
                'message': f'Score cannot exceed question point value of {exam_question.points}'
            }), 400
            
        # Validate score is not negative
        if score < 0:
            return jsonify({
                'success': False,
                'message': 'Score cannot be negative'
            }), 400
            
        # Update the score
        student_answer.score = score
        
        # For multiple choice and true/false questions, update is_correct based on score
        if question.question_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
            student_answer.is_correct = (score > 0)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Answer graded successfully',
            'answer': {
                'id': student_answer.id,
                'student_id': student_answer.student_id,
                'exam_id': student_answer.exam_id,
                'question_id': student_answer.question_id,
                'answer_text': student_answer.answer_text,
                'is_correct': student_answer.is_correct,
                'score': student_answer.score
            }
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
        logging.error(f"Error grading answer: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while grading the answer',
            'error': str(e)
        }), 500 