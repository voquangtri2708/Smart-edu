from flask import request

def paginate_query(query, default_page_size=10):
    """
    Phân trang cho SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        default_page_size: Kích thước trang mặc định
        
    Returns:
        paginated_query: Query đã được phân trang
        pagination_info: Dictionary chứa thông tin phân trang
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', default_page_size, type=int)
    
    # Giới hạn kích thước trang để tránh quá tải
    page_size = min(page_size, 100)
    
    # Đảm bảo page và page_size luôn dương
    page = max(1, page)
    page_size = max(1, page_size)
    
    # Tính total items và total pages
    total_items = query.count()
    total_pages = (total_items + page_size - 1) // page_size
    
    # Thực hiện phân trang
    paginated_query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Thông tin phân trang
    pagination_info = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }
    
    return paginated_query, pagination_info

def get_pagination_response(items, pagination_info):
    """
    Trả về response đã được phân trang
    
    Args:
        items: Danh sách items đã được phân trang
        pagination_info: Thông tin phân trang từ hàm paginate_query
        
    Returns:
        Dictionary chứa data và thông tin phân trang
    """
    return {
        "data": items,
        "pagination": pagination_info
    } 