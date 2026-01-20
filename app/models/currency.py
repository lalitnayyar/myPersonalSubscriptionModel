"""Currency rate model."""
from datetime import datetime
from app import db


class CurrencyRate(db.Model):
    """Currency exchange rates."""

    __tablename__ = 'currency_rates'

    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('from_currency', 'to_currency', name='unique_currency_pair'),
    )

    @staticmethod
    def get_rate(from_currency, to_currency):
        """Get exchange rate between two currencies."""
        if from_currency == to_currency:
            return 1.0

        rate = CurrencyRate.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency
        ).first()

        if rate:
            return rate.rate

        # Try inverse
        inverse_rate = CurrencyRate.query.filter_by(
            from_currency=to_currency,
            to_currency=from_currency
        ).first()

        if inverse_rate:
            return 1.0 / inverse_rate.rate

        # Default to 1 if rate not found
        return 1.0

    @staticmethod
    def update_rate(from_currency, to_currency, rate):
        """Update or create exchange rate."""
        existing = CurrencyRate.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency
        ).first()

        if existing:
            existing.rate = rate
            existing.updated_at = datetime.utcnow()
        else:
            new_rate = CurrencyRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate
            )
            db.session.add(new_rate)

        db.session.commit()

    @staticmethod
    def get_default_rates():
        """Return default exchange rates (USD base)."""
        return [
            {'from_currency': 'USD', 'to_currency': 'EUR', 'rate': 0.92},
            {'from_currency': 'USD', 'to_currency': 'GBP', 'rate': 0.79},
            {'from_currency': 'USD', 'to_currency': 'INR', 'rate': 83.12},
            {'from_currency': 'USD', 'to_currency': 'CAD', 'rate': 1.36},
            {'from_currency': 'USD', 'to_currency': 'AUD', 'rate': 1.53},
            {'from_currency': 'USD', 'to_currency': 'JPY', 'rate': 149.50},
            {'from_currency': 'EUR', 'to_currency': 'GBP', 'rate': 0.86},
            {'from_currency': 'EUR', 'to_currency': 'INR', 'rate': 90.35},
        ]

    def __repr__(self):
        return f'<CurrencyRate {self.from_currency}/{self.to_currency}: {self.rate}>'
