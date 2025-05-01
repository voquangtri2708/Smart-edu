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
    """
    Get feedback statistics by month/quarter/year.
    Query parameters:
    - month: (optional) Month number (1-12)
    - quarter: (optional) Quarter number (1-4)
    - year: (optional) Year (e.g. 2023)
    - teacher_id: (optional) Teacher ID to filter by
    - classroom_id: (optional) Classroom ID to filter by
    
    If only month is provided, current year is used.
    If only quarter is provided, current year is used.
    If neither month, quarter, nor year is provided, current month and year are used.
    """
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
                    Classroom.classroom_name,
                    func.count(Feedback.id).label('count')
                ).join(
                    Feedback, Feedback.classroom_id == Classroom.id
                ).filter(
                    Feedback.sentiment == sentiment_type,
                    Feedback.feedback_type == 'CLASSROOM',
                    *query_filters
                ).group_by(
                    Classroom.id
                ).order_by(
                    func.count(Feedback.id).desc()
                ).limit(1).first()
                
                if classroom_query:
                    c_id, c_name, count = classroom_query
                    top_classrooms[sentiment_type.lower()] = {
                        'id': c_id,
                        'name': c_name,
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

@feedback_stats_bp.route('/admin/stats/feedback/detailed', methods=['GET'])
@auth_required
@admin_required
def get_detailed_feedback_stats():
    """
    Get detailed feedback statistics with teacher and classroom breakdown.
    Query parameters:
    - month: (optional) Month number (1-12)
    - quarter: (optional) Quarter number (1-4)
    - year: (optional) Year (e.g. 2023)
    - page: (optional) Page number for pagination
    - per_page: (optional) Number of items per page
    - sentiment: (optional) Filter sentiment type (positive, neutral, negative)
    """
    try:
        # Log request parameters để debug
        print("DEBUG - GET /admin/stats/feedback/detailed")
        print("DEBUG - Request params:", request.args.to_dict())
        
        # Get filter params
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        quarter = request.args.get('quarter', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        classroom_id = request.args.get('classroom_id', type=int)
        
        # Get pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get sentiment filter
        sentiment_filter = request.args.get('sentiment')
        
        # Get teacher specific params
        teacher_page = request.args.get('teacher_page', page, type=int)
        teacher_per_page = request.args.get('teacher_per_page', per_page, type=int) 
        teacher_sentiment = request.args.get('teacher_sentiment', sentiment_filter)
        teacher_sort = request.args.get('teacher_sort', 'count')  # Mặc định sắp xếp theo count
        teacher_sort_direction = request.args.get('teacher_sort_direction', 'desc')  # Mặc định giảm dần
        
        # Get classroom specific params
        classroom_page = request.args.get('classroom_page', page, type=int)
        classroom_per_page = request.args.get('classroom_per_page', per_page, type=int)
        classroom_sentiment = request.args.get('classroom_sentiment', sentiment_filter)
        classroom_sort = request.args.get('classroom_sort', 'count')  # Mặc định sắp xếp theo count
        classroom_sort_direction = request.args.get('classroom_sort_direction', 'desc')  # Mặc định giảm dần
        
        # Validate and prepare date filters
        query_filters = []
        period_label = ''
        
        if year:
            period_label = str(year)
            query_filters.append(func.extract('year', Feedback.created_at) == year)
            
            if month:
                period_label += f"-{month:02d}"
                query_filters.append(func.extract('month', Feedback.created_at) == month)
            elif quarter:
                start_month = (quarter - 1) * 3 + 1
                end_month = start_month + 2
                period_label += f" Q{quarter}"
                query_filters.append(func.extract('month', Feedback.created_at).between(start_month, end_month))
        else:
            # Default to current year
            current_year = datetime.now().year
            period_label = str(current_year)
            query_filters.append(func.extract('year', Feedback.created_at) == current_year)
            
        # Apply teacher or classroom filter if provided
        if teacher_id:
            query_filters.append(Feedback.teacher_id == teacher_id)
            
        if classroom_id:
            query_filters.append(Feedback.classroom_id == classroom_id)
            
        # Get all teachers and classrooms for dropdown lists
        try:
            teachers_list = db.session.query(
                Teacher.id,
                Teacher.first_name,
                Teacher.last_name
            ).order_by(
                Teacher.last_name,
                Teacher.first_name
            ).all()
            
            teachers_for_dropdown = [
                {
                    'id': t_id,
                    'first_name': t_first,
                    'last_name': t_last,
                    'name': f"{t_last} {t_first}"
                }
                for t_id, t_first, t_last in teachers_list
            ]
                
            classrooms_list = db.session.query(
                Classroom.id,
                Classroom.room_number,
                Building.name,
                Building.id,
                Campus.name,
                Campus.id
            ).join(
                Building, Classroom.building_id == Building.id
            ).join(
                Campus, Building.campus_id == Campus.id
            ).order_by(
                Campus.name,
                Building.name,
                Classroom.room_number
            ).all()
            
            classrooms_for_dropdown = [
                {
                    'id': c_id,
                    'room_number': c_room,
                    'building_name': b_name,
                    'building_id': b_id,
                    'campus_name': camp_name,
                    'campus_id': camp_id,
                    'name': f"{c_room} - {b_name} ({camp_name})"
                }
                for c_id, c_room, b_name, b_id, camp_name, camp_id in classrooms_list
            ]
        except Exception as e:
            teachers_for_dropdown = []
            classrooms_for_dropdown = []
        
        # Get sentiment trend by day during the period
        try:
            sentiment_trends = db.session.query(
                func.date(Feedback.created_at).label('date'),
                Feedback.sentiment,
                func.count(Feedback.id).label('count')
            ).filter(
                *query_filters
            ).group_by(
                'date',
                Feedback.sentiment
            ).order_by(
                'date'
            ).all()
        except Exception as e:
            sentiment_trends = []
        
        # Process sentiment trends
        date_sentiment_map = {}
        for date_obj, sentiment, count in sentiment_trends:
            try:
                date_str = date_obj.strftime('%Y-%m-%d')
                if date_str not in date_sentiment_map:
                    date_sentiment_map[date_str] = {
                        'date': date_str,
                        'POSITIVE': 0,
                        'NEUTRAL': 0,
                        'NEGATIVE': 0
                    }
                date_sentiment_map[date_str][sentiment] = count
            except Exception as e:
                pass
        
        sentiment_trend_data = list(date_sentiment_map.values())
        sentiment_trend_data.sort(key=lambda x: x['date'])
        
        # Get top teachers and classrooms with most positive, negative, and neutral feedback
        top_teachers_by_sentiment = {}
        
        for sentiment_type in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
            # Skip if teacher sentiment filter is provided and doesn't match
            if teacher_sentiment and teacher_sentiment.upper() != sentiment_type:
                top_teachers_by_sentiment[sentiment_type.lower()] = []
                continue
                
            try:
                # Calculate total count and page offset for pagination
                total_query = db.session.query(func.count(Teacher.id)).join(
                    Feedback, Feedback.teacher_id == Teacher.id
                ).filter(
                    Feedback.sentiment == sentiment_type,
                    Feedback.feedback_type == 'TEACHER',
                    *query_filters
                ).group_by(Teacher.id)
                
                total_count = len(db.session.execute(total_query).all())
                offset = (teacher_page - 1) * teacher_per_page
                
                # In thông tin debug để xem hướng sắp xếp
                print(f"DEBUG - Teacher sort: field={teacher_sort}, direction={teacher_sort_direction}")
                
                # Lấy tất cả các giảng viên theo sentiment này để sắp xếp thủ công trong Python
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
                ).all()
                
                # Thực hiện sắp xếp thủ công
                teacher_results = []
                for t_id, t_first, t_last, count in teacher_query:
                    teacher_results.append({
                        'id': t_id, 
                        'first_name': t_first,
                        'last_name': t_last,
                        'count': count
                    })
                
                # Sắp xếp danh sách theo count
                if teacher_sort_direction and teacher_sort_direction.lower() == 'asc':
                    print(f"DEBUG - Sorting teachers by count ASC")
                    teacher_results.sort(key=lambda x: x['count'])
                else:
                    print(f"DEBUG - Sorting teachers by count DESC")
                    teacher_results.sort(key=lambda x: x['count'], reverse=True)
                
                # Áp dụng phân trang
                paginated_results = teacher_results[offset:offset+teacher_per_page]
                
                # Ghi log
                print(f"DEBUG - Teacher results after sorting ({len(paginated_results)} items):")
                for idx, teacher in enumerate(paginated_results):
                    print(f"  {idx+1}. {teacher['last_name']} {teacher['first_name']} - count: {teacher['count']}")
                
                # Chuyển đổi sang định dạng API
                top_teachers_by_sentiment[sentiment_type.lower()] = [
                    {
                        'id': teacher['id'], 
                        'name': f"{teacher['last_name']} {teacher['first_name']}", 
                        'count': teacher['count'],
                        'sentiment': sentiment_type.lower()
                    } 
                    for teacher in paginated_results
                ]
                
                # Add pagination info
                if teacher_sentiment and teacher_sentiment.upper() == sentiment_type:
                    top_teachers_by_sentiment['pagination'] = {
                        'total': total_count,
                        'page': teacher_page,
                        'per_page': teacher_per_page,
                        'pages': (total_count + teacher_per_page - 1) // teacher_per_page
                    }
            except Exception as e:
                top_teachers_by_sentiment[sentiment_type.lower()] = []
        
        top_classrooms_by_sentiment = {}
        
        for sentiment_type in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
            # Skip if classroom sentiment filter is provided and doesn't match
            if classroom_sentiment and classroom_sentiment.upper() != sentiment_type:
                top_classrooms_by_sentiment[sentiment_type.lower()] = []
                continue
                
            try:
                # Calculate total count and page offset for pagination
                total_query = db.session.query(func.count(Classroom.id)).join(
                    Feedback, Feedback.classroom_id == Classroom.id
                ).filter(
                    Feedback.sentiment == sentiment_type,
                    Feedback.feedback_type == 'CLASSROOM',
                    *query_filters
                ).group_by(Classroom.id)
                
                total_count = len(db.session.execute(total_query).all())
                offset = (classroom_page - 1) * classroom_per_page
                
                # In thông tin debug để xem hướng sắp xếp
                print(f"DEBUG - Classroom sort: field={classroom_sort}, direction={classroom_sort_direction}")
                
                # Lấy tất cả các phòng học theo sentiment này để sắp xếp thủ công trong Python
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
                    Classroom.id,
                    Building.id,
                    Campus.id
                ).all()
                
                # Thực hiện sắp xếp thủ công
                classroom_results = []
                for c_id, c_room, b_name, camp_name, count in classroom_query:
                    classroom_results.append({
                        'id': c_id, 
                        'room_number': c_room,
                        'building_name': b_name,
                        'campus_name': camp_name,
                        'count': count
                    })
                
                # Sắp xếp danh sách theo count
                if classroom_sort_direction and classroom_sort_direction.lower() == 'asc':
                    print(f"DEBUG - Sorting classrooms by count ASC")
                    classroom_results.sort(key=lambda x: x['count'])
                else:
                    print(f"DEBUG - Sorting classrooms by count DESC")
                    classroom_results.sort(key=lambda x: x['count'], reverse=True)
                
                # Áp dụng phân trang
                paginated_results = classroom_results[offset:offset+classroom_per_page]
                
                # Ghi log
                print(f"DEBUG - Classroom results after sorting ({len(paginated_results)} items):")
                for idx, classroom in enumerate(paginated_results):
                    print(f"  {idx+1}. {classroom['room_number']} - {classroom['building_name']} - count: {classroom['count']}")
                
                # Chuyển đổi sang định dạng API
                top_classrooms_by_sentiment[sentiment_type.lower()] = [
                    {
                        'id': classroom['id'], 
                        'room_number': classroom['room_number'],
                        'building_name': classroom['building_name'],
                        'campus_name': classroom['campus_name'],
                        'name': f"{classroom['room_number']} - {classroom['building_name']} ({classroom['campus_name']})",
                        'count': classroom['count'],
                        'sentiment': sentiment_type.lower()
                    } 
                    for classroom in paginated_results
                ]
                
                # Add pagination info
                if classroom_sentiment and classroom_sentiment.upper() == sentiment_type:
                    top_classrooms_by_sentiment['pagination'] = {
                        'total': total_count,
                        'page': classroom_page,
                        'per_page': classroom_per_page,
                        'pages': (total_count + classroom_per_page - 1) // classroom_per_page
                    }
            except Exception as e:
                top_classrooms_by_sentiment[sentiment_type.lower()] = []
        
        response_data = {
            'period': period_label,
            'sentiment_trend': sentiment_trend_data,
            'all_teachers': teachers_for_dropdown,
            'all_classrooms': classrooms_for_dropdown,
            'top_teachers_by_sentiment': top_teachers_by_sentiment,
            'top_classrooms_by_sentiment': top_classrooms_by_sentiment
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@feedback_stats_bp.route('/admin/stats/feedback/top-teachers', methods=['GET'])
@auth_required
@admin_required
def get_top_teachers():
    """
    Get top teachers by sentiment.
    Query parameters:
    - month: (optional) Month number (1-12)
    - quarter: (optional) Quarter number (1-4)
    - year: (optional) Year (e.g. 2023)
    """
    try:
        # Get query parameters
        month = request.args.get('month', type=int)
        quarter = request.args.get('quarter', type=int)
        year = request.args.get('year', type=int)
        
        # Validate parameters
        current_date = datetime.now()
        current_year = current_date.year
        
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
        
        # Apply filters based on provided parameters
        if month and not quarter:
            query_filters.append(extract('month', Feedback.created_at) == month)
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
            
        # Get teacher statistics with all sentiment counts
        try:
            teacher_stats = db.session.query(
                Teacher.id,
                Teacher.first_name,
                Teacher.last_name,
                func.count(Feedback.id).label('total_feedbacks'),
                func.sum(case([(Feedback.sentiment == 'POSITIVE', 1)], else_=0)).label('positive_count'),
                func.sum(case([(Feedback.sentiment == 'NEUTRAL', 1)], else_=0)).label('neutral_count'),
                func.sum(case([(Feedback.sentiment == 'NEGATIVE', 1)], else_=0)).label('negative_count')
            ).outerjoin(
                Feedback, and_(Feedback.teacher_id == Teacher.id, Feedback.feedback_type == 'TEACHER', *query_filters)
            ).group_by(
                Teacher.id
            ).order_by(
                func.count(Feedback.id).desc()
            ).all()
        except Exception as e:
            teacher_stats = []
        
        teacher_data = []
        for t_id, t_first_name, t_last_name, t_total, t_pos, t_neut, t_neg in teacher_stats:
            try:
                # Calculate sentiment ratio for visualization
                sentiment_ratio = {
                    'positive': float(t_pos / t_total) if t_total > 0 else 0,
                    'neutral': float(t_neut / t_total) if t_total > 0 else 0,
                    'negative': float(t_neg / t_total) if t_total > 0 else 0
                }
                
                teacher_data.append({
                    'id': t_id,
                    'name': f"{t_last_name} {t_first_name}",
                    'total_feedbacks': int(t_total or 0),
                    'sentiment_counts': {
                        'positive': int(t_pos or 0),
                        'neutral': int(t_neut or 0),
                        'negative': int(t_neg or 0)
                    },
                    'sentiment_ratio': sentiment_ratio
                })
            except Exception as e:
                pass
                
        return jsonify({
            'teacher_statistics': teacher_data
        })
    
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500

@feedback_stats_bp.route('/admin/stats/feedback/top-classrooms', methods=['GET'])
@auth_required
@admin_required
def get_top_classrooms():
    """
    Get top classrooms by sentiment.
    Query parameters:
    - month: (optional) Month number (1-12)
    - quarter: (optional) Quarter number (1-4)
    - year: (optional) Year (e.g. 2023)
    """
    try:
        # Get query parameters
        month = request.args.get('month', type=int)
        quarter = request.args.get('quarter', type=int)
        year = request.args.get('year', type=int)
        
        # Validate parameters
        current_date = datetime.now()
        current_year = current_date.year
        
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
        
        # Apply filters based on provided parameters
        if month and not quarter:
            query_filters.append(extract('month', Feedback.created_at) == month)
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
            
        # Get classroom statistics with building and campus info
        try:
            classroom_stats = db.session.query(
                Classroom.id,
                Classroom.room_number,
                Building.name.label('building_name'),
                Campus.name.label('campus_name'),
                func.count(Feedback.id).label('total_feedbacks'),
                func.sum(case([(Feedback.sentiment == 'POSITIVE', 1)], else_=0)).label('positive_count'),
                func.sum(case([(Feedback.sentiment == 'NEUTRAL', 1)], else_=0)).label('neutral_count'),
                func.sum(case([(Feedback.sentiment == 'NEGATIVE', 1)], else_=0)).label('negative_count')
            ).outerjoin(
                Feedback, and_(Feedback.classroom_id == Classroom.id, Feedback.feedback_type == 'CLASSROOM', *query_filters)
            ).join(
                Building, Classroom.building_id == Building.id
            ).join(
                Campus, Building.campus_id == Campus.id
            ).group_by(
                Classroom.id,
                Building.id,
                Campus.id
            ).order_by(
                func.count(Feedback.id).desc()
            ).all()
        except Exception as e:
            classroom_stats = []
        
        classroom_data = []
        for c_id, c_room, b_name, camp_name, c_total, c_pos, c_neut, c_neg in classroom_stats:
            try:
                # Calculate sentiment ratio for visualization
                sentiment_ratio = {
                    'positive': float(c_pos / c_total) if c_total > 0 else 0,
                    'neutral': float(c_neut / c_total) if c_total > 0 else 0,
                    'negative': float(c_neg / c_total) if c_total > 0 else 0
                }
                
                classroom_data.append({
                    'id': c_id,
                    'room_number': c_room,
                    'building_name': b_name,
                    'campus_name': camp_name,
                    'name': f"{c_room} - {b_name} ({camp_name})",
                    'total_feedbacks': int(c_total or 0),
                    'sentiment_counts': {
                        'positive': int(c_pos or 0),
                        'neutral': int(c_neut or 0),
                        'negative': int(c_neg or 0)
                    },
                    'sentiment_ratio': sentiment_ratio
                })
            except Exception as e:
                pass
                
        return jsonify({
            'classroom_statistics': classroom_data
        })
    
    except Exception as e:
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500 