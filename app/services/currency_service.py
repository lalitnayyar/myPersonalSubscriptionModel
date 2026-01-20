"""Currency service for conversion operations."""
from app import db
from app.models.currency import CurrencyRate


class CurrencyService:
    """Service for currency operations."""

    # Currency symbols for display
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '\u20ac',
        'GBP': '\u00a3',
        'INR': '\u20b9',
        'CAD': 'C$',
        'AUD': 'A$',
        'JPY': '\u00a5',
    }

    @staticmethod
    def convert(amount, from_currency, to_currency):
        """Convert amount from one currency to another."""
        if from_currency == to_currency:
            return amount

        rate = CurrencyRate.get_rate(from_currency, to_currency)
        return round(amount * rate, 2)

    @staticmethod
    def get_symbol(currency_code):
        """Get currency symbol for display."""
        return CurrencyService.CURRENCY_SYMBOLS.get(currency_code, currency_code)

    @staticmethod
    def format_amount(amount, currency_code):
        """Format amount with currency symbol."""
        symbol = CurrencyService.get_symbol(currency_code)
        if currency_code == 'JPY':
            return f'{symbol}{int(amount):,}'
        return f'{symbol}{amount:,.2f}'

    @staticmethod
    def seed_default_rates():
        """Seed default currency rates."""
        default_rates = CurrencyRate.get_default_rates()

        for rate_data in default_rates:
            existing = CurrencyRate.query.filter_by(
                from_currency=rate_data['from_currency'],
                to_currency=rate_data['to_currency']
            ).first()

            if not existing:
                rate = CurrencyRate(**rate_data)
                db.session.add(rate)

        db.session.commit()

    @staticmethod
    def get_all_rates_for_currency(base_currency):
        """Get all exchange rates from a base currency."""
        rates = {}
        rates[base_currency] = 1.0

        for rate in CurrencyRate.query.filter_by(from_currency=base_currency).all():
            rates[rate.to_currency] = rate.rate

        # Also get inverse rates
        for rate in CurrencyRate.query.filter_by(to_currency=base_currency).all():
            if rate.from_currency not in rates:
                rates[rate.from_currency] = 1.0 / rate.rate

        return rates
