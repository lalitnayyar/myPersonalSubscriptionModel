"""Payment method model."""
from datetime import datetime
from app import db


class PaymentMethod(db.Model):
    """Payment method model for tracking cards and bank accounts."""

    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # card, bank
    name = db.Column(db.String(100), nullable=False)  # e.g., "HDFC Credit Card"
    last_four_digits = db.Column(db.String(4))
    expiry_date = db.Column(db.Date, nullable=True)  # For cards
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='payment_method', lazy='dynamic')

    def get_display_name(self):
        """Get formatted display name."""
        if self.last_four_digits:
            return f'{self.name} (**** {self.last_four_digits})'
        return self.name

    def is_expiring_soon(self, days=30):
        """Check if card is expiring within specified days."""
        if not self.expiry_date:
            return False
        today = datetime.utcnow().date()
        delta = self.expiry_date - today
        return 0 <= delta.days <= days

    def is_expired(self):
        """Check if card has expired."""
        if not self.expiry_date:
            return False
        today = datetime.utcnow().date()
        return self.expiry_date < today

    def get_subscriptions_count(self):
        """Get count of subscriptions using this payment method."""
        return self.subscriptions.filter_by(status='active').count()

    def get_total_monthly_amount(self, currency='USD'):
        """Calculate total monthly amount charged to this payment method."""
        total = 0
        for sub in self.subscriptions.filter_by(status='active'):
            total += sub.get_monthly_amount(currency)
        return round(total, 2)

    @staticmethod
    def set_as_default(user_id, payment_method_id):
        """Set a payment method as default for user."""
        # Remove default from all user's payment methods
        PaymentMethod.query.filter_by(user_id=user_id).update({'is_default': False})
        # Set the specified one as default
        pm = PaymentMethod.query.get(payment_method_id)
        if pm and pm.user_id == user_id:
            pm.is_default = True
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<PaymentMethod {self.name}>'
