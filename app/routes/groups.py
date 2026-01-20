"""Subscription groups/bundles routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import SubscriptionGroup, Subscription

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/groups')
@login_required
def index():
    """List all subscription groups."""
    groups = current_user.subscription_groups.all()
    return render_template('groups/index.html', groups=groups)


@groups_bp.route('/groups/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new subscription group."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Group name is required.', 'danger')
            return redirect(url_for('groups.add'))

        group = SubscriptionGroup(
            user_id=current_user.id,
            name=name,
            description=description
        )
        db.session.add(group)
        db.session.commit()

        flash(f'Group "{name}" created successfully.', 'success')
        return redirect(url_for('groups.view', id=group.id))

    return render_template('groups/form.html', group=None, mode='add')


@groups_bp.route('/groups/<int:id>')
@login_required
def view(id):
    """View subscription group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    subscriptions = group.subscriptions.all()
    monthly_total = group.get_total_monthly_cost(current_user.default_currency)

    return render_template('groups/view.html',
                           group=group,
                           subscriptions=subscriptions,
                           monthly_total=monthly_total)


@groups_bp.route('/groups/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit subscription group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':
        group.name = request.form.get('name', '').strip()
        group.description = request.form.get('description', '').strip()

        db.session.commit()

        flash('Group updated successfully.', 'success')
        return redirect(url_for('groups.view', id=group.id))

    return render_template('groups/form.html', group=group, mode='edit')


@groups_bp.route('/groups/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete subscription group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    # Remove group from subscriptions
    for sub in group.subscriptions:
        sub.group_id = None

    name = group.name
    db.session.delete(group)
    db.session.commit()

    flash(f'Group "{name}" deleted.', 'success')
    return redirect(url_for('groups.index'))


@groups_bp.route('/groups/<int:id>/add-subscription', methods=['POST'])
@login_required
def add_subscription(id):
    """Add subscription to group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    subscription_id = request.form.get('subscription_id')
    if subscription_id:
        subscription = Subscription.query.filter_by(
            id=subscription_id, user_id=current_user.id
        ).first()

        if subscription:
            subscription.group_id = group.id
            db.session.commit()
            flash(f'"{subscription.name}" added to group.', 'success')

    return redirect(url_for('groups.view', id=group.id))


@groups_bp.route('/groups/<int:id>/remove-subscription/<int:sub_id>', methods=['POST'])
@login_required
def remove_subscription(id, sub_id):
    """Remove subscription from group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    subscription = Subscription.query.filter_by(
        id=sub_id, user_id=current_user.id, group_id=group.id
    ).first()

    if subscription:
        subscription.group_id = None
        db.session.commit()
        flash(f'"{subscription.name}" removed from group.', 'success')

    return redirect(url_for('groups.view', id=group.id))


@groups_bp.route('/groups/<int:id>/available-subscriptions')
@login_required
def available_subscriptions(id):
    """Get subscriptions not in any group."""
    group = SubscriptionGroup.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    subscriptions = current_user.subscriptions.filter(
        (Subscription.group_id == None) | (Subscription.group_id == group.id)
    ).all()

    return render_template('groups/available_subscriptions.html',
                           group=group,
                           subscriptions=subscriptions)
