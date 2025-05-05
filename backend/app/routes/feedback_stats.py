from flask import Blueprint, request, jsonify
from app import db
from app.models.feedback import Feedback
from app.models.teacher import Teacher
from app.models.classroom import Classroom
from app.models.building import Building
from app.models.campus import Campus
from app.utils.auth import auth_required, admin_required
from sqlalchemy import func, extract, case, and_, or_, outerjoin
from datetime import datetime, date
import calendar

feedback_stats_bp = Blueprint('feedback_stats', __name__)

@feedback_stats_bp.route('/admin/stats/feedback', methods=['GET'])
@auth_required
@admin_required
def get_feedback_stats():
    try:
        # Get query parameters
        month = request.args.get('month', type=int)
        quarter = request.args.get('quarter', type=int)
        year = request.args.get('year', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        classroom_id = request.args.get('classroom_id', type=int)
        
        # Validate parameters
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        if month and (month < 1 or month > 12):
            return jsonify({"message": "Tháng không hợp lệ. Vui lòng chọn từ 1-12."}), 400
        
        if quarter and (quarter < 1 or quarter > 4):
            return jsonify({"message": "Quý không hợp lệ. Vui lòng chọn từ 1-4."}), 400
        
        # Set default values if not provided
        if not year:
            year = current_year
        
        # Base query - Fixed by creating a proper query object
        base_year_filter = extract('year', Feedback.created_at) == year
        query_filters = [base_year_filter]
        
        period_type = "year"
        period_label = f"Năm {year}"
        
        # Apply filters based on provided parameters
        if month and not quarter:
            query_filters.append(extract('month', Feedback.created_at) == month)
            period_type = "month"
            period_label = f"Tháng {month}/{year}"
        elif quarter and not month:
            if quarter == 1:
                months = [1, 2, 3]
            elif quarter == 2:
                months = [4, 5, 6]
            elif quarter == 3:
                months = [7, 8, 9]
            else:  # quarter == 4
                months = [10, 11, 12]
            
            query_filters.append(extract('month', Feedback.created_at).in_(months))
            period_type = "quarter"
            period_label = f"Quý {quarter}/{year}"
        elif not month and not quarter:
            period_type = "year"
            period_label = f"Năm {year}"
            
        # Apply teacher or classroom filter if provided
        if teacher_id:
            query_filters.append(Feedback.teacher_id == teacher_id)
            
        if classroom_id:
            query_filters.append(Feedback.classroom_id == classroom_id)
        
        # Get the total number of feedbacks
        try:
            total_feedbacks = db.session.query(func.count(Feedback.id)).filter(*query_filters).scalar() or 0
        except Exception as e:
            total_feedbacks = 0
        
        # Get feedback count by type
        try:
            feedback_by_type = db.session.query(
                Feedback.feedback_type,
                func.count(Feedback.id)
            ).filter(
                *query_filters
            ).group_by(
                Feedback.feedback_type
            ).all()
        except Exception as e:
            feedback_by_type = []
        
        feedback_type_data = {
            'TEACHER': 0,
            'CLASSROOM': 0
        }
        
        for fb_type, count in feedback_by_type:
            feedback_type_data[fb_type] = count
        
        # Get feedback count by sentiment
        try:
            feedback_by_sentiment = db.session.query(
                Feedback.sentiment,
                func.count(Feedback.id)
            ).filter(
                *query_filters
            ).group_by(
                Feedback.sentiment
            ).all()
        except Exception as e:
            feedback_by_sentiment = []
        
        sentiment_data = {
            'POSITIVE': 0,
            'NEUTRAL': 0,
            'NEGATIVE': 0
        }
        
        for sentiment, count in feedback_by_sentiment:
            sentiment_data[sentiment] = count
            
        # Get top teachers with most positive, negative, and neutral feedback
        top_teachers = {}
        try:
            for sentiment_type in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
                teacher_query = db.session.query(
                    Teacher.id,
                    Teacher.first_name,
                    Teacher.last_name,
                    func.count(Feedback.id).label('count')
                ).join(
                    Feedback, Feedback.teacher_id == Teacher.id
                ).filter(
                    Feedback.sentiment == sentiment_type,
                    Feedback.feedback_type == 'TEACHER',
                    *query_filters
                ).group_by(
                    Teacher.id
                ).order_by(
                    func.count(Feedback.id).desc()
                ).limit(1).first()
                
                if teacher_query:
                    t_id, t_first, t_last, count = teacher_query
                    top_teachers[sentiment_type.lower()] = {
                        'id': t_id,
                        'name': f"{t_last} {t_first}",
                        'count': count
                    }
                else:
                    top_teachers[sentiment_type.lower()] = None
        except Exception as e:
            pass
            
        # Get top classrooms with most positive, negative, and neutral feedback
        top_classrooms = {}
        try:
            for sentiment_type in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
                classroom_query = db.session.query(
                    Classroom.id,
                    Classroom.room_number,
                    Building.name.label('building_name'),
                    Campus.name.label('campus_name'),
                    func.count(Feedback.id).label('count')
                ).join(
                    Feedback, Feedback.classroom_id == Classroom.id
                ).join(
                    Building, Classroom.building_id == Building.id
                ).join(
                    Campus, Building.campus_id == Campus.id
                ).filter(
                    Feedback.sentiment == sentiment_type,
                    Feedback.feedback_type == 'CLASSROOM',
                    *query_filters
                ).group_by(
                    Classroom.id, Building.name, Campus.name
                ).order_by(
                    func.count(Feedback.id).desc()
                ).limit(1).first()
                
                if classroom_query:
                    c_id, room_num, building_name, campus_name, count = classroom_query
                    top_classrooms[sentiment_type.lower()] = {
                        'id': c_id,
                        'name': f"Phòng {room_num} - {building_name} - {campus_name}",
                        'count': count
                    }
                else:
                    top_classrooms[sentiment_type.lower()] = None
        except Exception as e:
            pass
        
        # Get feedback trend over time (by month within the year, or by day within month/quarter)
        time_series_data = []
        
        if period_type == "year":
            try:
                # Group by month for yearly view
                feedback_by_month = db.session.query(
                    extract('month', Feedback.created_at).label('month'),
                    func.count(Feedback.id)
                ).filter(
                    *query_filters
                ).group_by(
                    'month'
                ).order_by(
                    'month'
                ).all()
                
                # Fill in all months
                month_data = {month: 0 for month in range(1, 13)}
                for month_num, count in feedback_by_month:
                    month_data[month_num] = count
                
                for month_num in range(1, 13):
                    month_name = calendar.month_name[month_num]
                    time_series_data.append({
                        'period': f'{month_name}',
                        'count': month_data[month_num]
                    })
            except Exception as e:
                pass
        
        elif period_type == "quarter":
            try:
                # For quarterly view, group by month within that quarter
                months_in_quarter = {
                    1: [1, 2, 3],
                    2: [4, 5, 6],
                    3: [7, 8, 9],
                    4: [10, 11, 12]
                }.get(quarter)
                
                feedback_by_month = db.session.query(
                    extract('month', Feedback.created_at).label('month'),
                    func.count(Feedback.id)
                ).filter(
                    *query_filters
                ).group_by(
                    'month'
                ).order_by(
                    'month'
                ).all()
                
                # Fill in months for this quarter
                month_data = {month: 0 for month in months_in_quarter}
                for month_num, count in feedback_by_month:
                    if month_num in months_in_quarter:
                        month_data[month_num] = count
                
                for month_num in months_in_quarter:
                    month_name = calendar.month_name[month_num]
                    time_series_data.append({
                        'period': f'{month_name}',
                        'count': month_data[month_num]
                    })
            except Exception as e:
                pass
        
        elif period_type == "month":
            try:
                # For monthly view, group by day within that month
                _, days_in_month = calendar.monthrange(year, month)
                
                feedback_by_day = db.session.query(
                    extract('day', Feedback.created_at).label('day'),
                    func.count(Feedback.id)
                ).filter(
                    *query_filters
                ).group_by(
                    'day'
                ).order_by(
                    'day'
                ).all()
                
                # Fill in all days
                day_data = {day: 0 for day in range(1, days_in_month + 1)}
                for day_num, count in feedback_by_day:
                    day_data[day_num] = count
                
                for day_num in range(1, days_in_month + 1):
                    time_series_data.append({
                        'period': f'Ngày {day_num}',
                        'count': day_data[day_num]
                    })
            except Exception as e:
                pass
        
        # Return the statistics
        response_data = {
            'period': period_label,
            'total_feedbacks': total_feedbacks,
            'feedback_by_type': feedback_type_data,
            'feedback_by_sentiment': sentiment_data,
            'time_series_data': time_series_data,
            'top_teachers_by_sentiment': top_teachers,
            'top_classrooms_by_sentiment': top_classrooms
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500