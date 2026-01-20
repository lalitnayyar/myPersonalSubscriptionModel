"""Payment methods management routes."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import PaymentMethod, Subscription

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/payment-methods')
@login_required
def index():
    """List all payment methods."""
    payment_methods = current_user.payment_methods.all()
    return render_template('payments/index.html', payment_methods=payment_methods)


@payments_bp.route('/payment-methods/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new payment method."""
    if request.method == 'POST':
        pm_type = request.form.get('type', 'card')
        name = request.form.get('name', '').strip()
        last_four_digits = request.form.get('last_four_digits', '').strip()
        expiry_date_str = request.form.get('expiry_date')
        is_default = request.form.get('is_default') == 'on'

        # Validation
        if not name:
            flash('Payment method name is required.', 'danger')
            return redirect(url_for('payments.add'))

        if last_four_digits and (not last_four_digits.isdigit() or len(last_four_digits) != 4):
            flash('Please enter exactly 4 digits.', 'danger')
            return redirect(url_for('payments.add'))

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m').date()
                # Set to last day of month
                if expiry_date.month == 12:
                    expiry_date = expiry_date.replace(day=31)
                else:
                    expiry_date = expiry_date.replace(
                        month=expiry_date.month + 1,
                        day=1
                    )
                    from datetime import timedelta
                    expiry_date = expiry_date - timedelta(days=1)
            except ValueError:
                pass

        # If setting as default, unset others
        if is_default:
            current_user.payment_methods.update({'is_default': False})

        payment_method = PaymentMethod(
            user_id=current_user.id,
            type=pm_type,
            name=name,
            last_four_digits=last_four_digits or None,
            expiry_date=expiry_date,
            is_default=is_default
        )

        db.session.add(payment_method)
        db.session.commit()

        flash(f'Payment method "{name}" added successfully.', 'success')
        return redirect(url_for('payments.index'))

    return render_template('payments/form.html', payment_method=None, mode='add')


@payments_bp.route('/payment-methods/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit payment method."""
    payment_method = PaymentMethod.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':
        payment_method.type = request.form.get('type', 'card')
        payment_method.name = request.form.get('name', '').strip()
        payment_method.last_four_digits = request.form.get('last_four_digits', '').strip() or None
        is_default = request.form.get('is_default') == 'on'

        expiry_date_str = request.form.get('expiry_date')
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m').date()
                if expiry_date.month == 12:
                    payment_method.expiry_date = expiry_date.replace(day=31)
                else:
                    payment_method.expiry_date = expiry_date.replace(
                        month=expiry_date.month + 1,
                        day=1
                    )
                    from datetime import timedelta
                    payment_method.expiry_date = payment_method.expiry_date - timedelta(days=1)
            except ValueError:
                payment_method.expiry_date = None
        else:
            payment_method.expiry_date = None

        # Handle default status
        if is_default:
            current_user.payment_methods.filter(
                PaymentMethod.id != payment_method.id
            ).update({'is_default': False})
        payment_method.is_default = is_default

        db.session.commit()

        flash('Payment method updated successfully.', 'success')
        return redirect(url_for('payments.index'))

    return render_template('payments/form.html', payment_method=payment_method, mode='edit')


@payments_bp.route('/payment-methods/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete payment method."""
    payment_method = PaymentMethod.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    # Check if any subscriptions are using this payment method
    subs_count = payment_method.subscriptions.count()
    if subs_count > 0:
        flash(f'Cannot delete: {subs_count} subscription(s) are using this payment method.', 'danger')
        return redirect(url_for('payments.index'))

    name = payment_method.name
    db.session.delete(payment_method)
    db.session.commit()

    flash(f'Payment method "{name}" deleted successfully.', 'success')
    return redirect(url_for('payments.index'))


@payments_bp.route('/payment-methods/<int:id>/set-default', methods=['POST'])
@login_required
def set_default(id):
    """Set payment method as default."""
    payment_method = PaymentMethod.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    PaymentMethod.set_as_default(current_user.id, payment_method.id)

    flash(f'"{payment_method.name}" is now your default payment method.', 'success')
    return redirect(url_for('payments.index'))


@payments_bp.route('/payment-methods/<int:id>/subscriptions')
@login_required
def subscriptions(id):
    """View subscriptions for a payment method."""
    payment_method = PaymentMethod.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    subscriptions = payment_method.subscriptions.filter_by(user_id=current_user.id).all()

    return render_template('payments/subscriptions.html',
                           payment_method=payment_method,
                           subscriptions=subscriptions)
