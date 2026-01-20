"""User model."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and profile."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    default_currency = db.Column(db.String(3), default='USD')
    email_alerts_enabled = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    dark_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic',
                                    cascade='all, delete-orphan')
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy='dynamic',
                                      cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic',
                                    cascade='all, delete-orphan')
    subscription_groups = db.relationship('SubscriptionGroup', backref='user', lazy='dynamic',
                                          cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_active_subscriptions_count(self):
        """Get count of active subscriptions."""
        from app.models.subscription import Subscription
        return self.subscriptions.filter_by(status='active').count()

    def get_monthly_spend(self, currency=None):
        """Calculate total monthly spend in specified currency."""
        from app.models.subscription import Subscription
        currency = currency or self.default_currency
        total = 0

        active_subs = self.subscriptions.filter_by(status='active').all()
        for sub in active_subs:
            if sub.billing_cycle == 'monthly':
                amount = sub.get_amount_in_currency(currency)
            elif sub.billing_cycle == 'yearly':
                amount = sub.get_amount_in_currency(currency) / 12
            else:  # one_time - don't include in monthly
                amount = 0
            total += amount

        return round(total, 2)

    def __repr__(self):
        return f'<User {self.email}>'
