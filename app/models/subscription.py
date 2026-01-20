"""Subscription related models."""
from datetime import datetime, timedelta
from app import db


class SubscriptionGroup(db.Model):
    """Group/Bundle for related subscriptions."""

    __tablename__ = 'subscription_groups'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    subscriptions = db.relationship('Subscription', backref='group', lazy='dynamic')

    def get_total_monthly_cost(self, currency='USD'):
        """Calculate total monthly cost of all subscriptions in group."""
        total = 0
        for sub in self.subscriptions.filter_by(status='active'):
            if sub.billing_cycle == 'monthly':
                total += sub.get_amount_in_currency(currency)
            elif sub.billing_cycle == 'yearly':
                total += sub.get_amount_in_currency(currency) / 12
        return round(total, 2)

    def __repr__(self):
        return f'<SubscriptionGroup {self.name}>'


class Subscription(db.Model):
    """Main subscription model."""

    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subscription_type_id = db.Column(db.Integer, db.ForeignKey('subscription_types.id'))
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('subscription_groups.id'), nullable=True)

    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    billing_cycle = db.Column(db.String(20), default='monthly')  # one_time, monthly, yearly

    start_date = db.Column(db.Date, nullable=False)
    next_renewal_date = db.Column(db.Date)
    reminder_days = db.Column(db.Integer, default=15)

    status = db.Column(db.String(20), default='active')  # active, inactive, cancelled
    auto_renew = db.Column(db.Boolean, default=True)

    # Trial tracking
    is_trial = db.Column(db.Boolean, default=False)
    trial_end_date = db.Column(db.Date, nullable=True)

    # Encrypted credentials (stored as encrypted strings)
    account_email_encrypted = db.Column(db.Text, nullable=True)
    account_username_encrypted = db.Column(db.Text, nullable=True)

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    price_history = db.relationship('SubscriptionPriceHistory', backref='subscription',
                                    lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('SubscriptionAttachment', backref='subscription',
                                  lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='subscription',
                                    lazy='dynamic', cascade='all, delete-orphan')

    def get_amount_in_currency(self, target_currency):
        """Convert amount to target currency."""
        if self.currency == target_currency:
            return self.amount

        from app.models.currency import CurrencyRate
        rate = CurrencyRate.get_rate(self.currency, target_currency)
        return round(self.amount * rate, 2)

    def get_monthly_amount(self, currency=None):
        """Get equivalent monthly amount."""
        currency = currency or self.currency
        amount = self.get_amount_in_currency(currency)

        if self.billing_cycle == 'yearly':
            return round(amount / 12, 2)
        elif self.billing_cycle == 'monthly':
            return amount
        else:
            return 0  # one_time subscriptions don't have monthly cost

    def get_yearly_amount(self, currency=None):
        """Get equivalent yearly amount."""
        currency = currency or self.currency
        amount = self.get_amount_in_currency(currency)

        if self.billing_cycle == 'monthly':
            return round(amount * 12, 2)
        elif self.billing_cycle == 'yearly':
            return amount
        else:
            return 0  # one_time subscriptions don't have yearly cost

    def days_until_renewal(self):
        """Calculate days until next renewal."""
        if not self.next_renewal_date:
            return None
        today = datetime.utcnow().date()
        delta = self.next_renewal_date - today
        return delta.days

    def is_due_soon(self, days=15):
        """Check if subscription is due within specified days."""
        days_left = self.days_until_renewal()
        if days_left is None:
            return False
        return 0 <= days_left <= days

    def is_overdue(self):
        """Check if subscription renewal is overdue."""
        days_left = self.days_until_renewal()
        if days_left is None:
            return False
        return days_left < 0

    def is_trial_ending_soon(self, days=7):
        """Check if trial is ending within specified days."""
        if not self.is_trial or not self.trial_end_date:
            return False
        today = datetime.utcnow().date()
        delta = self.trial_end_date - today
        return 0 <= delta.days <= days

    def update_price(self, new_amount, reason=None):
        """Update price and track history."""
        if new_amount != self.amount:
            # Create price history record
            history = SubscriptionPriceHistory(
                subscription_id=self.id,
                old_amount=self.amount,
                new_amount=new_amount,
                currency=self.currency,
                reason=reason
            )
            db.session.add(history)
            self.amount = new_amount

    def calculate_next_renewal(self):
        """Calculate the next renewal date based on billing cycle."""
        if self.billing_cycle == 'one_time':
            self.next_renewal_date = None
        elif self.billing_cycle == 'monthly':
            if self.next_renewal_date:
                # Add one month
                next_month = self.next_renewal_date.month % 12 + 1
                year_add = 1 if self.next_renewal_date.month == 12 else 0
                try:
                    self.next_renewal_date = self.next_renewal_date.replace(
                        month=next_month,
                        year=self.next_renewal_date.year + year_add
                    )
                except ValueError:
                    # Handle months with fewer days
                    import calendar
                    last_day = calendar.monthrange(
                        self.next_renewal_date.year + year_add, next_month
                    )[1]
                    self.next_renewal_date = self.next_renewal_date.replace(
                        month=next_month,
                        year=self.next_renewal_date.year + year_add,
                        day=min(self.next_renewal_date.day, last_day)
                    )
        elif self.billing_cycle == 'yearly':
            if self.next_renewal_date:
                try:
                    self.next_renewal_date = self.next_renewal_date.replace(
                        year=self.next_renewal_date.year + 1
                    )
                except ValueError:
                    # Handle Feb 29 in leap years
                    self.next_renewal_date = self.next_renewal_date.replace(
                        year=self.next_renewal_date.year + 1,
                        day=28
                    )

    def reactivate(self, new_start_date=None):
        """Reactivate an inactive subscription."""
        self.status = 'active'
        if new_start_date:
            self.start_date = new_start_date
            self.next_renewal_date = new_start_date
            self.calculate_next_renewal()

    def __repr__(self):
        return f'<Subscription {self.name}>'


class SubscriptionPriceHistory(db.Model):
    """Track price changes for subscriptions."""

    __tablename__ = 'subscription_price_history'

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    old_amount = db.Column(db.Float, nullable=False)
    new_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<PriceHistory {self.subscription_id}: {self.old_amount} -> {self.new_amount}>'


class SubscriptionAttachment(db.Model):
    """Attachments for subscriptions (receipts, invoices, etc.)."""

    __tablename__ = 'subscription_attachments'

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename (UUID)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20))  # receipt, invoice, contract, other
    file_size = db.Column(db.Integer)  # in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def get_file_size_display(self):
        """Get human readable file size."""
        if self.file_size < 1024:
            return f'{self.file_size} B'
        elif self.file_size < 1024 * 1024:
            return f'{self.file_size / 1024:.1f} KB'
        else:
            return f'{self.file_size / (1024 * 1024):.1f} MB'

    def __repr__(self):
        return f'<Attachment {self.original_filename}>'
