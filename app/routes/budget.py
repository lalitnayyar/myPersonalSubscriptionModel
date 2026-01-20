"""Budget planning routes."""
from datetime import datetime, timedelta
import calendar
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Subscription
from app.services.currency_service import CurrencyService

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/budget')
@login_required
def index():
    """Budget overview and planning page."""
    currency = current_user.default_currency

    # Get current month and year
    today = datetime.utcnow().date()
    current_month = request.args.get('month', today.month, type=int)
    current_year = request.args.get('year', today.year, type=int)

    # Get calendar data
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]

    # Get subscriptions due this month
    first_day = datetime(current_year, current_month, 1).date()
    if current_month == 12:
        last_day = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(current_year, current_month + 1, 1).date() - timedelta(days=1)

    renewals_this_month = current_user.subscriptions.filter(
        Subscription.status == 'active',
        Subscription.next_renewal_date >= first_day,
        Subscription.next_renewal_date <= last_day
    ).order_by(Subscription.next_renewal_date).all()

    # Group by day
    renewals_by_day = {}
    for sub in renewals_this_month:
        day = sub.next_renewal_date.day
        if day not in renewals_by_day:
            renewals_by_day[day] = []
        renewals_by_day[day].append(sub)

    # Calculate monthly totals
    monthly_total = sum(
        sub.get_amount_in_currency(currency)
        for sub in renewals_this_month
    )

    # Get spending breakdown
    recurring_monthly = current_user.get_monthly_spend(currency)

    # Navigation
    prev_month = current_month - 1
    prev_year = current_year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = current_month + 1
    next_year = current_year
    if next_month > 12:
        next_month = 1
        next_year += 1

    return render_template('budget/index.html',
                           month_name=month_name,
                           current_month=current_month,
                           current_year=current_year,
                           month_days=month_days,
                           renewals_by_day=renewals_by_day,
                           monthly_total=monthly_total,
                           recurring_monthly=recurring_monthly,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=today,
                           currency=currency)


@budget_bp.route('/budget/yearly')
@login_required
def yearly():
    """Yearly budget overview."""
    currency = current_user.default_currency
    today = datetime.utcnow().date()
    current_year = request.args.get('year', today.year, type=int)

    months_data = []

    for month in range(1, 13):
        first_day = datetime(current_year, month, 1).date()
        if month == 12:
            last_day = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(current_year, month + 1, 1).date() - timedelta(days=1)

        # Get renewals for this month
        renewals = current_user.subscriptions.filter(
            Subscription.status == 'active',
            Subscription.next_renewal_date >= first_day,
            Subscription.next_renewal_date <= last_day
        ).all()

        month_total = sum(
            sub.get_amount_in_currency(currency)
            for sub in renewals
        )

        months_data.append({
            'month': month,
            'name': calendar.month_abbr[month],
            'total': month_total,
            'count': len(renewals)
        })

    yearly_total = sum(m['total'] for m in months_data)
    monthly_average = yearly_total / 12

    return render_template('budget/yearly.html',
                           months_data=months_data,
                           yearly_total=yearly_total,
                           monthly_average=monthly_average,
                           current_year=current_year,
                           currency=currency)


@budget_bp.route('/budget/forecast')
@login_required
def forecast():
    """Budget forecast for upcoming months."""
    currency = current_user.default_currency
    today = datetime.utcnow().date()

    # Forecast next 6 months
    forecast_data = []

    for i in range(6):
        month = today.month + i
        year = today.year

        while month > 12:
            month -= 12
            year += 1

        first_day = datetime(year, month, 1).date()
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

        # Get expected renewals
        renewals = current_user.subscriptions.filter(
            Subscription.status == 'active',
            Subscription.next_renewal_date >= first_day,
            Subscription.next_renewal_date <= last_day
        ).all()

        month_total = sum(
            sub.get_amount_in_currency(currency)
            for sub in renewals
        )

        forecast_data.append({
            'month': f'{calendar.month_name[month]} {year}',
            'total': month_total,
            'subscriptions': renewals
        })

    total_forecast = sum(f['total'] for f in forecast_data)

    return render_template('budget/forecast.html',
                           forecast_data=forecast_data,
                           total_forecast=total_forecast,
                           currency=currency)
