"""Notification routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def index():
    """View all notifications."""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all')
    show_read = request.args.get('show_read', 'true').lower() == 'true'

    query = current_user.notifications

    if filter_type != 'all':
        query = query.filter_by(type=filter_type)

    if not show_read:
        query = query.filter_by(is_read=False)

    notifications = query.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    # Get unread count
    unread_count = current_user.notifications.filter_by(is_read=False).count()

    return render_template('notifications/index.html',
                           notifications=notifications,
                           unread_count=unread_count,
                           filter_type=filter_type,
                           show_read=show_read)


@notifications_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    """Mark notification as read."""
    notification = Notification.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    notification.mark_as_read()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    return redirect(url_for('notifications.index'))


@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read."""
    Notification.mark_all_as_read(current_user.id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a notification."""
    notification = Notification.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    db.session.delete(notification)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/notifications/dropdown')
@login_required
def dropdown():
    """Get notifications for dropdown (AJAX)."""
    notifications = Notification.get_unread_for_user(current_user.id, limit=5)
    unread_count = current_user.notifications.filter_by(is_read=False).count()

    return jsonify({
        'unread_count': unread_count,
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'message': n.message,
            'icon': n.get_icon(),
            'color': n.get_color(),
            'created_at': n.created_at.strftime('%b %d, %H:%M'),
            'subscription_id': n.subscription_id
        } for n in notifications]
    })
