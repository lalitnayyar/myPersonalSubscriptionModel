"""Subscription management routes."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (
    Subscription, Category, Provider, SubscriptionType,
    PaymentMethod, SubscriptionGroup, SubscriptionPriceHistory
)
from app.services.encryption_service import encrypt_credential, decrypt_credential
from app.services.notification_service import NotificationService

subscriptions_bp = Blueprint('subscriptions', __name__)


@subscriptions_bp.route('/subscriptions')
@login_required
def index():
    """List all subscriptions."""
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'name')

    query = current_user.subscriptions

    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if category_filter != 'all':
        query = query.filter_by(category_id=int(category_filter))

    # Apply sorting
    if sort_by == 'name':
        query = query.order_by(Subscription.name)
    elif sort_by == 'amount':
        query = query.order_by(Subscription.amount.desc())
    elif sort_by == 'renewal':
        query = query.order_by(Subscription.next_renewal_date)
    elif sort_by == 'created':
        query = query.order_by(Subscription.created_at.desc())

    subscriptions = query.all()
    categories = Category.query.all()

    return render_template('subscriptions/index.html',
                           subscriptions=subscriptions,
                           categories=categories,
                           status_filter=status_filter,
                           category_filter=category_filter,
                           sort_by=sort_by)


@subscriptions_bp.route('/subscriptions/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new subscription."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        provider_id = request.form.get('provider_id') or None
        category_id = request.form.get('category_id') or None
        subscription_type_id = request.form.get('subscription_type_id') or None
        payment_method_id = request.form.get('payment_method_id') or None
        group_id = request.form.get('group_id') or None

        amount = float(request.form.get('amount', 0))
        currency = request.form.get('currency', current_user.default_currency)
        billing_cycle = request.form.get('billing_cycle', 'monthly')

        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        next_renewal_date_str = request.form.get('next_renewal_date')
        if next_renewal_date_str:
            next_renewal_date = datetime.strptime(next_renewal_date_str, '%Y-%m-%d').date()
        else:
            next_renewal_date = start_date

        reminder_days = int(request.form.get('reminder_days', 15))
        auto_renew = request.form.get('auto_renew') == 'on'

        # Trial info
        is_trial = request.form.get('is_trial') == 'on'
        trial_end_date = None
        if is_trial and request.form.get('trial_end_date'):
            trial_end_date = datetime.strptime(request.form.get('trial_end_date'), '%Y-%m-%d').date()

        # Credentials (encrypted)
        account_email = request.form.get('account_email', '').strip()
        account_username = request.form.get('account_username', '').strip()

        notes = request.form.get('notes', '').strip()

        # Validation
        if not name:
            flash('Subscription name is required.', 'danger')
            return redirect(url_for('subscriptions.add'))

        if amount < 0:
            flash('Amount cannot be negative.', 'danger')
            return redirect(url_for('subscriptions.add'))

        # Create subscription
        subscription = Subscription(
            user_id=current_user.id,
            name=name,
            provider_id=provider_id,
            category_id=category_id,
            subscription_type_id=subscription_type_id,
            payment_method_id=payment_method_id,
            group_id=group_id,
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            start_date=start_date,
            next_renewal_date=next_renewal_date,
            reminder_days=reminder_days,
            auto_renew=auto_renew,
            is_trial=is_trial,
            trial_end_date=trial_end_date,
            account_email_encrypted=encrypt_credential(account_email) if account_email else None,
            account_username_encrypted=encrypt_credential(account_username) if account_username else None,
            notes=notes,
            status='active'
        )

        db.session.add(subscription)
        db.session.commit()

        flash(f'Subscription "{name}" added successfully.', 'success')
        return redirect(url_for('subscriptions.view', id=subscription.id))

    # GET request
    categories = Category.query.all()
    providers = Provider.query.order_by(Provider.name).all()
    subscription_types = SubscriptionType.query.all()
    payment_methods = current_user.payment_methods.all()
    groups = current_user.subscription_groups.all()

    return render_template('subscriptions/form.html',
                           subscription=None,
                           categories=categories,
                           providers=providers,
                           subscription_types=subscription_types,
                           payment_methods=payment_methods,
                           groups=groups,
                           mode='add')


@subscriptions_bp.route('/subscriptions/<int:id>')
@login_required
def view(id):
    """View subscription details."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # Decrypt credentials for display
    account_email = decrypt_credential(subscription.account_email_encrypted)
    account_username = decrypt_credential(subscription.account_username_encrypted)

    # Get price history
    price_history = subscription.price_history.order_by(
        SubscriptionPriceHistory.changed_at.desc()
    ).limit(10).all()

    # Get attachments
    attachments = subscription.attachments.all()

    return render_template('subscriptions/view.html',
                           subscription=subscription,
                           account_email=account_email,
                           account_username=account_username,
                           price_history=price_history,
                           attachments=attachments)


@subscriptions_bp.route('/subscriptions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit subscription."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        # Get form data
        subscription.name = request.form.get('name', '').strip()
        subscription.provider_id = request.form.get('provider_id') or None
        subscription.category_id = request.form.get('category_id') or None
        subscription.subscription_type_id = request.form.get('subscription_type_id') or None
        subscription.payment_method_id = request.form.get('payment_method_id') or None
        subscription.group_id = request.form.get('group_id') or None

        new_amount = float(request.form.get('amount', 0))
        price_change_reason = request.form.get('price_change_reason', '').strip()

        # Track price change
        if new_amount != subscription.amount:
            old_amount = subscription.amount
            subscription.update_price(new_amount, price_change_reason)
            NotificationService.create_price_change_notification(
                subscription, old_amount, new_amount
            )

        subscription.currency = request.form.get('currency', current_user.default_currency)
        subscription.billing_cycle = request.form.get('billing_cycle', 'monthly')

        subscription.start_date = datetime.strptime(
            request.form.get('start_date'), '%Y-%m-%d'
        ).date()

        next_renewal_str = request.form.get('next_renewal_date')
        if next_renewal_str:
            subscription.next_renewal_date = datetime.strptime(next_renewal_str, '%Y-%m-%d').date()

        subscription.reminder_days = int(request.form.get('reminder_days', 15))
        subscription.auto_renew = request.form.get('auto_renew') == 'on'

        # Trial info
        subscription.is_trial = request.form.get('is_trial') == 'on'
        if subscription.is_trial and request.form.get('trial_end_date'):
            subscription.trial_end_date = datetime.strptime(
                request.form.get('trial_end_date'), '%Y-%m-%d'
            ).date()
        elif not subscription.is_trial:
            subscription.trial_end_date = None

        # Credentials
        account_email = request.form.get('account_email', '').strip()
        account_username = request.form.get('account_username', '').strip()
        subscription.account_email_encrypted = encrypt_credential(account_email) if account_email else None
        subscription.account_username_encrypted = encrypt_credential(account_username) if account_username else None

        subscription.notes = request.form.get('notes', '').strip()

        db.session.commit()

        flash('Subscription updated successfully.', 'success')
        return redirect(url_for('subscriptions.view', id=subscription.id))

    # GET request
    categories = Category.query.all()
    providers = Provider.query.order_by(Provider.name).all()
    subscription_types = SubscriptionType.query.all()
    payment_methods = current_user.payment_methods.all()
    groups = current_user.subscription_groups.all()

    # Decrypt credentials
    account_email = decrypt_credential(subscription.account_email_encrypted)
    account_username = decrypt_credential(subscription.account_username_encrypted)

    return render_template('subscriptions/form.html',
                           subscription=subscription,
                           categories=categories,
                           providers=providers,
                           subscription_types=subscription_types,
                           payment_methods=payment_methods,
                           groups=groups,
                           account_email=account_email,
                           account_username=account_username,
                           mode='edit')


@subscriptions_bp.route('/subscriptions/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete subscription."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    name = subscription.name

    db.session.delete(subscription)
    db.session.commit()

    flash(f'Subscription "{name}" deleted successfully.', 'success')
    return redirect(url_for('subscriptions.index'))


@subscriptions_bp.route('/subscriptions/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Toggle subscription status (active/inactive)."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if subscription.status == 'active':
        subscription.status = 'inactive'
        flash(f'"{subscription.name}" marked as inactive.', 'info')
    else:
        subscription.status = 'active'
        flash(f'"{subscription.name}" marked as active.', 'success')

    db.session.commit()

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': subscription.status})

    return redirect(url_for('subscriptions.view', id=subscription.id))


@subscriptions_bp.route('/subscriptions/<int:id>/reactivate', methods=['GET', 'POST'])
@login_required
def reactivate(id):
    """Reactivate an inactive subscription."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if subscription.status == 'active':
        flash('This subscription is already active.', 'info')
        return redirect(url_for('subscriptions.view', id=subscription.id))

    if request.method == 'POST':
        new_start_date = datetime.strptime(
            request.form.get('new_start_date'), '%Y-%m-%d'
        ).date()

        subscription.reactivate(new_start_date)
        db.session.commit()

        flash(f'"{subscription.name}" has been reactivated.', 'success')
        return redirect(url_for('subscriptions.view', id=subscription.id))

    return render_template('subscriptions/reactivate.html', subscription=subscription)


@subscriptions_bp.route('/subscriptions/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel a subscription."""
    subscription = Subscription.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    subscription.status = 'cancelled'
    subscription.auto_renew = False
    db.session.commit()

    flash(f'"{subscription.name}" has been cancelled.', 'warning')
    return redirect(url_for('subscriptions.view', id=subscription.id))
