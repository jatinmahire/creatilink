"""Helper functions for creating and managing notifications"""
from datetime import datetime
from app import db
from app.models import Notification

def create_notification(user_id, notification_type, title, message, project_id=None, transaction_id=None):
    """Create a new notification for a user"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        project_id=project_id,
        transaction_id=transaction_id
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_unread_count(user_id):
    """Get count of unread notifications for a user"""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()

def mark_as_read(notification_id):
    """Mark a notification as read"""
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
    return notification

def get_user_notifications(user_id, limit=20):
    """Get recent notifications for a user"""
    return Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).limit(limit).all()
