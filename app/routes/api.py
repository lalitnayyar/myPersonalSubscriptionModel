"""REST API routes."""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Subscription, Category, Provider, Notification

api_bp = Blueprint('api', __name__)


@api_bp.route('/subscriptions')
@login_required
def get_subscriptions():
    """Get all subscriptions for current user."""
    status = request.args.get('status')
    category_id = request.args.get('category_id')

    query = current_user.subscriptions

    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    subscriptions = query.all()

    return jsonify([{
        'id': s.id,
        'name': s.name,
        'amount': s.amount,
        'currency': s.currency,
        'billing_cycle': s.billing_cycle,
        'status': s.status,
        'next_renewal_date': s.next_renewal_date.isoformat() if s.next_renewal_date else None,
        'category': s.category.name if s.category else None,
        'provider': s.provider.name if s.provider else None,
        'is_trial': s.is_trial,
        'days_until_renewal': s.days_until_renewal()
    } for s in subscriptions])


@api_bp.route('/subscriptions/<int:id>')
@login_required
def get_subscription(id):
    """Get single subscription."""
    subscription = Subscription.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    return jsonify({
        'id': subscription.id,
        'name': subscription.name,
        'amount': subscription.amount,
        'currency': subscription.currency,
        'billing_cycle': subscription.billing_cycle,
        'status': subscription.status,
        'start_date': subscription.start_date.isoformat(),
        'next_renewal_date': subscription.next_renewal_date.isoformat() if subscription.next_renewal_date else None,
        'reminder_days': subscription.reminder_days,
        'auto_renew': subscription.auto_renew,
        'is_trial': subscription.is_trial,
        'trial_end_date': subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
        'category_id': subscription.category_id,
        'provider_id': subscription.provider_id,
        'notes': subscription.notes
    })


@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics."""
    currency = current_user.default_currency

    active_count = current_user.subscriptions.filter_by(status='active').count()
    inactive_count = current_user.subscriptions.filter_by(status='inactive').count()
    monthly_spend = current_user.get_monthly_spend(currency)

    today = datetime.utcnow().date()
    upcoming_date = today + timedelta(days=15)

    upcoming_renewals = current_user.subscriptions.filter(
        Subscription.status == 'active',
        Subscription.next_renewal_date >= today,
        Subscription.next_renewal_date <= upcoming_date
    ).count()

    return jsonify({
        'active_count': active_count,
        'inactive_count': inactive_count,
        'monthly_spend': monthly_spend,
        'currency': currency,
        'upcoming_renewals': upcoming_renewals
    })


@api_bp.route('/categories')
@login_required
def get_categories():
    """Get all categories."""
    categories = Category.query.order_by(Category.name).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'icon': c.icon,
        'color': c.color,
        'description': c.description
    } for c in categories])


@api_bp.route('/providers')
@login_required
def get_providers():
    """Get all providers."""
    providers = Provider.query.order_by(Provider.name).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'website': p.website,
        'logo_url': p.logo_url
    } for p in providers])


@api_bp.route('/notifications')
@login_required
def get_notifications():
    """Get user notifications."""
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    limit = request.args.get('limit', 20, type=int)

    query = current_user.notifications

    if unread_only:
        query = query.filter_by(is_read=False)

    notifications = query.order_by(
        Notification.created_at.desc()
    ).limit(limit).all()

    return jsonify([{
        'id': n.id,
        'type': n.type,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat(),
        'subscription_id': n.subscription_id
    } for n in notifications])


@api_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_notification_read(id):
    """Mark notification as read."""
    notification = Notification.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    notification.mark_as_read()

    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    Notification.mark_all_as_read(current_user.id)
    return jsonify({'success': True})


@api_bp.route('/spending/by-category')
@login_required
def spending_by_category():
    """Get spending breakdown by category."""
    currency = current_user.default_currency
    categories = Category.query.all()

    data = []
    for category in categories:
        total = category.get_total_monthly_spend(current_user.id, currency)
        if total > 0:
            data.append({
                'category': category.name,
                'amount': total,
                'color': category.color
            })

    data.sort(key=lambda x: x['amount'], reverse=True)

    return jsonify({
        'currency': currency,
        'data': data
    })


@api_bp.route('/upcoming-renewals')
@login_required
def upcoming_renewals():
    """Get upcoming renewals."""
    days = request.args.get('days', 30, type=int)

    today = datetime.utcnow().date()
    end_date = today + timedelta(days=days)

    subscriptions = current_user.subscriptions.filter(
        Subscription.status == 'active',
        Subscription.next_renewal_date >= today,
        Subscription.next_renewal_date <= end_date
    ).order_by(Subscription.next_renewal_date).all()

    return jsonify([{
        'id': s.id,
        'name': s.name,
        'amount': s.amount,
        'currency': s.currency,
        'next_renewal_date': s.next_renewal_date.isoformat(),
        'days_until': s.days_until_renewal()
    } for s in subscriptions])
