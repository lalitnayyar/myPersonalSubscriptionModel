"""Provider, Category, and SubscriptionType models."""
from datetime import datetime
from app import db


class Category(db.Model):
    """Category for organizing subscriptions."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    icon = db.Column(db.String(50))  # Bootstrap icon class
    color = db.Column(db.String(7))  # Hex color code
    description = db.Column(db.String(255))

    # Relationships
    providers = db.relationship('Provider', backref='category', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='category', lazy='dynamic')

    def get_subscriptions_count(self, user_id=None):
        """Get count of subscriptions in this category."""
        query = self.subscriptions.filter_by(status='active')
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.count()

    def get_total_monthly_spend(self, user_id, currency='USD'):
        """Calculate total monthly spend for this category."""
        total = 0
        for sub in self.subscriptions.filter_by(user_id=user_id, status='active'):
            total += sub.get_monthly_amount(currency)
        return round(total, 2)

    @staticmethod
    def get_default_categories():
        """Return list of default categories to seed."""
        return [
            {'name': 'Entertainment', 'icon': 'bi-film', 'color': '#e74c3c',
             'description': 'Streaming services, gaming, etc.'},
            {'name': 'Productivity', 'icon': 'bi-briefcase', 'color': '#3498db',
             'description': 'Work and productivity tools'},
            {'name': 'Cloud Storage', 'icon': 'bi-cloud', 'color': '#9b59b6',
             'description': 'Cloud storage and backup services'},
            {'name': 'Music', 'icon': 'bi-music-note-beamed', 'color': '#1abc9c',
             'description': 'Music streaming services'},
            {'name': 'News & Media', 'icon': 'bi-newspaper', 'color': '#f39c12',
             'description': 'News subscriptions and media'},
            {'name': 'Health & Fitness', 'icon': 'bi-heart-pulse', 'color': '#e91e63',
             'description': 'Health and fitness apps'},
            {'name': 'Education', 'icon': 'bi-mortarboard', 'color': '#00bcd4',
             'description': 'Learning platforms and courses'},
            {'name': 'Utilities', 'icon': 'bi-gear', 'color': '#607d8b',
             'description': 'Utility services and tools'},
            {'name': 'Shopping', 'icon': 'bi-cart', 'color': '#ff9800',
             'description': 'Shopping memberships'},
            {'name': 'Other', 'icon': 'bi-three-dots', 'color': '#95a5a6',
             'description': 'Other subscriptions'},
        ]

    def __repr__(self):
        return f'<Category {self.name}>'


class Provider(db.Model):
    """Service provider/company."""

    __tablename__ = 'providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='provider', lazy='dynamic')

    def get_subscriptions_count(self, user_id=None):
        """Get count of subscriptions for this provider."""
        query = self.subscriptions.filter_by(status='active')
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.count()

    @staticmethod
    def get_default_providers():
        """Return list of default providers to seed."""
        return [
            {'name': 'Netflix', 'website': 'https://netflix.com'},
            {'name': 'Spotify', 'website': 'https://spotify.com'},
            {'name': 'Amazon Prime', 'website': 'https://amazon.com'},
            {'name': 'Disney+', 'website': 'https://disneyplus.com'},
            {'name': 'Microsoft 365', 'website': 'https://microsoft.com'},
            {'name': 'Google One', 'website': 'https://one.google.com'},
            {'name': 'Apple Music', 'website': 'https://apple.com/music'},
            {'name': 'iCloud+', 'website': 'https://apple.com/icloud'},
            {'name': 'YouTube Premium', 'website': 'https://youtube.com'},
            {'name': 'HBO Max', 'website': 'https://hbomax.com'},
            {'name': 'Dropbox', 'website': 'https://dropbox.com'},
            {'name': 'Adobe Creative Cloud', 'website': 'https://adobe.com'},
            {'name': 'Notion', 'website': 'https://notion.so'},
            {'name': 'Slack', 'website': 'https://slack.com'},
            {'name': 'GitHub', 'website': 'https://github.com'},
            {'name': 'Other', 'website': ''},
        ]

    def __repr__(self):
        return f'<Provider {self.name}>'


class SubscriptionType(db.Model):
    """Type/tier of subscription (Basic, Premium, etc.)."""

    __tablename__ = 'subscription_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))

    # Relationships
    subscriptions = db.relationship('Subscription', backref='subscription_type', lazy='dynamic')

    @staticmethod
    def get_default_types():
        """Return list of default subscription types."""
        return [
            {'name': 'Free', 'description': 'Free tier with limited features'},
            {'name': 'Basic', 'description': 'Entry-level paid subscription'},
            {'name': 'Standard', 'description': 'Standard subscription tier'},
            {'name': 'Premium', 'description': 'Premium tier with full features'},
            {'name': 'Enterprise', 'description': 'Enterprise/business tier'},
            {'name': 'Family', 'description': 'Family plan with multiple users'},
            {'name': 'Student', 'description': 'Discounted student plan'},
        ]

    def __repr__(self):
        return f'<SubscriptionType {self.name}>'
