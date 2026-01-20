"""Dashboard routes."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Subscription, Notification, Category

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page."""
    # Summary statistics
    active_count = current_user.subscriptions.filter_by(status='active').count()
    inactive_count = current_user.subscriptions.filter_by(status='inactive').count()
    trial_count = current_user.subscriptions.filter(
        Subscription.is_trial == True,
        Subscription.status == 'active'
    ).count()

    monthly_spend = current_user.get_monthly_spend(current_user.default_currency)
    yearly_spend = monthly_spend * 12

    # Upcoming renewals (next 15 days)
    today = datetime.utcnow().date()
    upcoming_date = today + timedelta(days=15)
    upcoming_renewals = current_user.subscriptions.filter(
        Subscription.status == 'active',
        Subscription.next_renewal_date.isnot(None),
        Subscription.next_renewal_date >= today,
        Subscription.next_renewal_date <= upcoming_date
    ).order_by(Subscription.next_renewal_date).limit(5).all()

    # Recent notifications
    recent_notifications = Notification.get_unread_for_user(current_user.id, limit=5)

    # Get spending by category for chart
    category_spending = get_category_spending()

    # Get monthly spending for last 6 months
    monthly_history = get_monthly_spending_history()

    return render_template('dashboard/index.html',
                           active_count=active_count,
                           inactive_count=inactive_count,
                           trial_count=trial_count,
                           monthly_spend=monthly_spend,
                           yearly_spend=yearly_spend,
                           upcoming_renewals=upcoming_renewals,
                           recent_notifications=recent_notifications,
                           category_spending=category_spending,
                           monthly_history=monthly_history)


def get_category_spending():
    """Get spending breakdown by category."""
    categories = Category.query.all()
    data = []

    for category in categories:
        total = category.get_total_monthly_spend(
            current_user.id,
            current_user.default_currency
        )
        if total > 0:
            data.append({
                'name': category.name,
                'amount': total,
                'color': category.color or '#6c757d'
            })

    # Sort by amount descending
    data.sort(key=lambda x: x['amount'], reverse=True)
    return data


def get_monthly_spending_history():
    """Get monthly spending for the last 6 months."""
    today = datetime.utcnow().date()
    months = []

    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i * 30)
        months.append({
            'label': month_date.strftime('%b'),
            'amount': current_user.get_monthly_spend(current_user.default_currency)
        })

    return months


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics."""
    active_count = current_user.subscriptions.filter_by(status='active').count()
    monthly_spend = current_user.get_monthly_spend(current_user.default_currency)

    return jsonify({
        'active_count': active_count,
        'monthly_spend': monthly_spend,
        'currency': current_user.default_currency
    })
