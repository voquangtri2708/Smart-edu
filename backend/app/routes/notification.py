from flask import Blueprint, request, jsonify
from app import db
from app.models.notification import Notification
from app.models.account import Account
from app.utils.auth import auth_required

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['POST'])
@auth_required
def create_notification():
    """Tạo mới một thông báo"""
    data = request.get_json()

    # Validate input
    if not data or 'account_id' not in data or 'message' not in data:
        return jsonify({"message": "Thiếu thông tin bắt buộc"}), 400

    # Check if account exists
    account = Account.query.get(data['account_id'])
    if not account:
        return jsonify({"message": "Tài khoản không tồn tại"}), 404

    # Create new notification
    new_notification = Notification(
        account_id=data['account_id'],
        message=data['message'],
        is_read=False  # Default trạng thái là chưa đọc
    )
    db.session.add(new_notification)
    db.session.commit()
    return jsonify({"message": "Notification created successfully"}), 201

@notification_bp.route('/notifications', methods=['GET'])
@auth_required
def get_notifications():
    """Lấy danh sách tất cả thông báo"""
    notifications = Notification.query.all()
    return jsonify([{
        "id": notification.id,
        "account_id": notification.account_id,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "updated_at": notification.updated_at
    } for notification in notifications])

@notification_bp.route('/notifications/<int:id>', methods=['GET'])
@auth_required
def get_notification(id):
    """Lấy thông tin chi tiết của một thông báo"""
    notification = Notification.query.get_or_404(id)
    return jsonify({
        "id": notification.id,
        "account_id": notification.account_id,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "updated_at": notification.updated_at
    })

@notification_bp.route('/notifications/<int:id>', methods=['PUT'])
@auth_required
def update_notification(id):
    """Cập nhật trạng thái thông báo"""
    data = request.get_json()
    notification = Notification.query.get_or_404(id)

    if 'is_read' in data:
        notification.is_read = data['is_read']

    db.session.commit()
    return jsonify({"message": "Notification updated successfully"})

@notification_bp.route('/notifications/<int:id>', methods=['DELETE'])
@auth_required
def delete_notification(id):
    """Xóa một thông báo"""
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "Notification deleted successfully"})