"""Notification service for creating and managing notifications."""
from datetime import datetime, timedelta
from app import db
from app.models import Notification, Subscription, User, PaymentMethod
from app.services.email_service import EmailService


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    def check_upcoming_renewals():
        """Check for subscriptions due for renewal and create notifications."""
        # Get all active subscriptions due within reminder days
        today = datetime.utcnow().date()
        users = User.query.all()

        for user in users:
            active_subs = Subscription.query.filter_by(
                user_id=user.id,
                status='active'
            ).filter(
                Subscription.next_renewal_date.isnot(None)
            ).all()

            for sub in active_subs:
                reminder_date = sub.next_renewal_date - timedelta(days=sub.reminder_days)

                if today >= reminder_date and sub.next_renewal_date >= today:
                    # Check if notification already exists for this renewal
                    existing = Notification.query.filter(
                        Notification.user_id == user.id,
                        Notification.subscription_id == sub.id,
                        Notification.type == Notification.TYPE_RENEWAL_REMINDER,
                        Notification.created_at >= datetime.utcnow() - timedelta(days=sub.reminder_days)
                    ).first()

                    if not existing:
                        days_until = (sub.next_renewal_date - today).days
                        message = f'{sub.name} is due for renewal in {days_until} days ({sub.currency} {sub.amount})'

                        notification = Notification.create_notification(
                            user_id=user.id,
                            notification_type=Notification.TYPE_RENEWAL_REMINDER,
                            message=message,
                            subscription_id=sub.id
                        )

                        # Send email if enabled
                        if user.email_alerts_enabled:
                            try:
                                if EmailService.send_renewal_reminder(user, sub):
                                    notification.email_sent = True
                                    db.session.commit()
                            except Exception:
                                pass  # Email sending is optional

    @staticmethod
    def check_trial_expirations():
        """Check for trials ending soon and create notifications."""
        today = datetime.utcnow().date()
        trial_warning_days = 7

        trial_subs = Subscription.query.filter(
            Subscription.is_trial == True,
            Subscription.trial_end_date.isnot(None),
            Subscription.status == 'active'
        ).all()

        for sub in trial_subs:
            days_until_trial_end = (sub.trial_end_date - today).days

            if 0 <= days_until_trial_end <= trial_warning_days:
                # Check if notification already exists
                existing = Notification.query.filter(
                    Notification.user_id == sub.user_id,
                    Notification.subscription_id == sub.id,
                    Notification.type == Notification.TYPE_TRIAL_ENDING,
                    Notification.created_at >= datetime.utcnow() - timedelta(days=trial_warning_days)
                ).first()

                if not existing:
                    message = f'Trial for {sub.name} ends in {days_until_trial_end} days'

                    Notification.create_notification(
                        user_id=sub.user_id,
                        notification_type=Notification.TYPE_TRIAL_ENDING,
                        message=message,
                        subscription_id=sub.id
                    )

    @staticmethod
    def check_expired_subscriptions():
        """Check for expired subscriptions and create notifications."""
        today = datetime.utcnow().date()

        expired_subs = Subscription.query.filter(
            Subscription.next_renewal_date < today,
            Subscription.status == 'active',
            Subscription.auto_renew == False
        ).all()

        for sub in expired_subs:
            # Check if notification already exists
            existing = Notification.query.filter(
                Notification.user_id == sub.user_id,
                Notification.subscription_id == sub.id,
                Notification.type == Notification.TYPE_EXPIRED,
                Notification.created_at >= datetime.utcnow() - timedelta(days=1)
            ).first()

            if not existing:
                message = f'{sub.name} has expired and needs attention'

                Notification.create_notification(
                    user_id=sub.user_id,
                    notification_type=Notification.TYPE_EXPIRED,
                    message=message,
                    subscription_id=sub.id
                )

    @staticmethod
    def check_payment_methods():
        """Check for expiring payment methods."""
        today = datetime.utcnow().date()
        warning_days = 30

        payment_methods = PaymentMethod.query.filter(
            PaymentMethod.expiry_date.isnot(None)
        ).all()

        for pm in payment_methods:
            days_until_expiry = (pm.expiry_date - today).days

            if 0 <= days_until_expiry <= warning_days:
                # Check if notification already exists
                existing = Notification.query.filter(
                    Notification.user_id == pm.user_id,
                    Notification.type == Notification.TYPE_CARD_EXPIRING,
                    Notification.message.contains(pm.name),
                    Notification.created_at >= datetime.utcnow() - timedelta(days=warning_days)
                ).first()

                if not existing:
                    message = f'Payment method {pm.get_display_name()} expires in {days_until_expiry} days'

                    Notification.create_notification(
                        user_id=pm.user_id,
                        notification_type=Notification.TYPE_CARD_EXPIRING,
                        message=message
                    )

    @staticmethod
    def run_all_checks():
        """Run all notification checks."""
        NotificationService.check_upcoming_renewals()
        NotificationService.check_trial_expirations()
        NotificationService.check_expired_subscriptions()
        NotificationService.check_payment_methods()

    @staticmethod
    def create_price_change_notification(subscription, old_amount, new_amount):
        """Create notification for price change."""
        message = f'{subscription.name} price changed from {subscription.currency} {old_amount} to {subscription.currency} {new_amount}'

        return Notification.create_notification(
            user_id=subscription.user_id,
            notification_type=Notification.TYPE_PRICE_CHANGE,
            message=message,
            subscription_id=subscription.id
        )
