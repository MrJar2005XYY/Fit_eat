from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User
from models.notification import Notification

notification_bp = Blueprint('notification', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@notification_bp.route('/', methods=['GET'])
def get_notifications():
    """获取通知列表"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    notifications = Notification.query.filter_by(user_id=user.id) \
        .order_by(Notification.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [n.to_dict() for n in notifications.items],
        'total': notifications.total,
        'unread': Notification.query.filter_by(user_id=user.id, is_read=False).count(),
    })


@notification_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """获取未读通知数量"""
    user = get_current_user()
    if not user:
        return jsonify({'count': 0})

    count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    return jsonify({'count': count})


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
def mark_read(notification_id):
    """标记通知为已读"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notification:
        return jsonify({'success': False, 'message': '通知不存在'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})


@notification_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    """标记所有通知为已读"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """删除通知"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notification:
        return jsonify({'success': False, 'message': '通知不存在'}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({'success': True})


def create_notification(user_id, type, title, content, link=''):
    """创建通知的工具函数"""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        link=link,
    )
    db.session.add(notification)
    db.session.commit()
    return notification
