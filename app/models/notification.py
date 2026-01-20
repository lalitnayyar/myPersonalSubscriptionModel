"""Notification model."""
from datetime import datetime
from app import db


class Notification(db.Model):
    """Notification model for alerts and reminders."""

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    type = db.Column(db.String(30), nullable=False)  # renewal_reminder, payment_due, expired, trial_ending
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)

    # Notification types
    TYPE_RENEWAL_REMINDER = 'renewal_reminder'
    TYPE_PAYMENT_DUE = 'payment_due'
    TYPE_EXPIRED = 'expired'
    TYPE_TRIAL_ENDING = 'trial_ending'
    TYPE_PRICE_CHANGE = 'price_change'
    TYPE_CARD_EXPIRING = 'card_expiring'

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def create_notification(user_id, notification_type, message, subscription_id=None):
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            subscription_id=subscription_id,
            type=notification_type,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_unread_for_user(user_id, limit=10):
        """Get unread notifications for a user."""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all_for_user(user_id, page=1, per_page=20):
        """Get all notifications for a user with pagination."""
        return Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user."""
        Notification.query.filter_by(user_id=user_id, is_read=False).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        db.session.commit()

    def get_icon(self):
        """Get icon class based on notification type."""
        icons = {
            self.TYPE_RENEWAL_REMINDER: 'bi-calendar-event',
            self.TYPE_PAYMENT_DUE: 'bi-credit-card',
            self.TYPE_EXPIRED: 'bi-exclamation-triangle',
            self.TYPE_TRIAL_ENDING: 'bi-clock-history',
            self.TYPE_PRICE_CHANGE: 'bi-currency-dollar',
            self.TYPE_CARD_EXPIRING: 'bi-credit-card-2-back',
        }
        return icons.get(self.type, 'bi-bell')

    def get_color(self):
        """Get color class based on notification type."""
        colors = {
            self.TYPE_RENEWAL_REMINDER: 'primary',
            self.TYPE_PAYMENT_DUE: 'warning',
            self.TYPE_EXPIRED: 'danger',
            self.TYPE_TRIAL_ENDING: 'info',
            self.TYPE_PRICE_CHANGE: 'secondary',
            self.TYPE_CARD_EXPIRING: 'warning',
        }
        return colors.get(self.type, 'secondary')

    def __repr__(self):
        return f'<Notification {self.type} for User {self.user_id}>'
