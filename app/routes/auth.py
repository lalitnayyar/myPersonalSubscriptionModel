"""Authentication routes."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Category, Provider, SubscriptionType
from app.models.currency import CurrencyRate
from app.services.currency_service import CurrencyService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.update_last_login()
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        default_currency = request.form.get('default_currency', 'USD')

        # Validation
        errors = []
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if not full_name:
            errors.append('Please enter your full name.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        # Create user
        user = User(
            email=email,
            full_name=full_name,
            default_currency=default_currency
        )
        user.set_password(password)

        # Make first user an admin
        if User.query.count() == 0:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        # Seed default data if needed
        seed_default_data()

        login_user(user)
        flash('Account created successfully! Welcome to Subscription Manager.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        default_currency = request.form.get('default_currency', 'USD')
        email_alerts_enabled = request.form.get('email_alerts_enabled') == 'on'
        dark_mode = request.form.get('dark_mode') == 'on'

        current_user.full_name = full_name
        current_user.default_currency = default_currency
        current_user.email_alerts_enabled = email_alerts_enabled
        current_user.dark_mode = dark_mode

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.profile'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('auth.profile'))


def seed_default_data():
    """Seed default categories, providers, and subscription types."""
    # Seed categories
    if Category.query.count() == 0:
        for cat_data in Category.get_default_categories():
            category = Category(**cat_data)
            db.session.add(category)
        db.session.commit()

    # Seed providers
    if Provider.query.count() == 0:
        for prov_data in Provider.get_default_providers():
            provider = Provider(**prov_data)
            db.session.add(provider)
        db.session.commit()

    # Seed subscription types
    if SubscriptionType.query.count() == 0:
        for type_data in SubscriptionType.get_default_types():
            sub_type = SubscriptionType(**type_data)
            db.session.add(sub_type)
        db.session.commit()

    # Seed currency rates
    CurrencyService.seed_default_rates()
