"""Admin panel routes."""
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from app import db
from app.models import User, Category, Provider, SubscriptionType

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard."""
    stats = {
        'users': User.query.count(),
        'categories': Category.query.count(),
        'providers': Provider.query.count(),
        'subscription_types': SubscriptionType.query.count()
    }
    return render_template('admin/index.html', stats=stats)


# ===== Categories =====
@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Manage categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add new category."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        icon = request.form.get('icon', '').strip()
        color = request.form.get('color', '#6c757d')
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.add_category'))

        if Category.query.filter_by(name=name).first():
            flash('Category with this name already exists.', 'danger')
            return redirect(url_for('admin.add_category'))

        category = Category(
            name=name,
            icon=icon,
            color=color,
            description=description
        )
        db.session.add(category)
        db.session.commit()

        flash(f'Category "{name}" created successfully.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=None, mode='add')


@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    """Edit category."""
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.icon = request.form.get('icon', '').strip()
        category.color = request.form.get('color', '#6c757d')
        category.description = request.form.get('description', '').strip()

        db.session.commit()

        flash('Category updated successfully.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=category, mode='edit')


@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    """Delete category."""
    category = Category.query.get_or_404(id)

    # Check if category is in use
    if category.subscriptions.count() > 0:
        flash('Cannot delete: category is in use by subscriptions.', 'danger')
        return redirect(url_for('admin.categories'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'Category "{name}" deleted.', 'success')
    return redirect(url_for('admin.categories'))


# ===== Providers =====
@admin_bp.route('/providers')
@login_required
@admin_required
def providers():
    """Manage providers."""
    providers = Provider.query.order_by(Provider.name).all()
    return render_template('admin/providers.html', providers=providers)


@admin_bp.route('/providers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_provider():
    """Add new provider."""
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        website = request.form.get('website', '').strip()
        category_id = request.form.get('category_id') or None
        logo_url = request.form.get('logo_url', '').strip()

        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                    unique_filename = f'{uuid.uuid4()}.{ext}'
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', unique_filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    file.save(filepath)
                    logo_url = f'/uploads/logos/{unique_filename}'

        if not name:
            flash('Provider name is required.', 'danger')
            return redirect(url_for('admin.add_provider'))

        if Provider.query.filter_by(name=name).first():
            flash('Provider with this name already exists.', 'danger')
            return redirect(url_for('admin.add_provider'))

        provider = Provider(
            name=name,
            website=website,
            category_id=category_id,
            logo_url=logo_url
        )
        db.session.add(provider)
        db.session.commit()

        flash(f'Provider "{name}" created successfully.', 'success')
        return redirect(url_for('admin.providers'))

    return render_template('admin/provider_form.html',
                           provider=None,
                           categories=categories,
                           mode='add')


@admin_bp.route('/providers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_provider(id):
    """Edit provider."""
    provider = Provider.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        provider.name = request.form.get('name', '').strip()
        provider.website = request.form.get('website', '').strip()
        provider.category_id = request.form.get('category_id') or None

        logo_url = request.form.get('logo_url', '').strip()
        if logo_url:
            provider.logo_url = logo_url

        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                    unique_filename = f'{uuid.uuid4()}.{ext}'
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', unique_filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    file.save(filepath)
                    provider.logo_url = f'/uploads/logos/{unique_filename}'

        db.session.commit()

        flash('Provider updated successfully.', 'success')
        return redirect(url_for('admin.providers'))

    return render_template('admin/provider_form.html',
                           provider=provider,
                           categories=categories,
                           mode='edit')


@admin_bp.route('/providers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_provider(id):
    """Delete provider."""
    provider = Provider.query.get_or_404(id)

    if provider.subscriptions.count() > 0:
        flash('Cannot delete: provider is in use by subscriptions.', 'danger')
        return redirect(url_for('admin.providers'))

    name = provider.name
    db.session.delete(provider)
    db.session.commit()

    flash(f'Provider "{name}" deleted.', 'success')
    return redirect(url_for('admin.providers'))


# ===== Subscription Types =====
@admin_bp.route('/subscription-types')
@login_required
@admin_required
def subscription_types():
    """Manage subscription types."""
    types = SubscriptionType.query.order_by(SubscriptionType.name).all()
    return render_template('admin/subscription_types.html', types=types)


@admin_bp.route('/subscription-types/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subscription_type():
    """Add new subscription type."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Type name is required.', 'danger')
            return redirect(url_for('admin.add_subscription_type'))

        if SubscriptionType.query.filter_by(name=name).first():
            flash('Subscription type with this name already exists.', 'danger')
            return redirect(url_for('admin.add_subscription_type'))

        sub_type = SubscriptionType(name=name, description=description)
        db.session.add(sub_type)
        db.session.commit()

        flash(f'Subscription type "{name}" created successfully.', 'success')
        return redirect(url_for('admin.subscription_types'))

    return render_template('admin/subscription_type_form.html', sub_type=None, mode='add')


@admin_bp.route('/subscription-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subscription_type(id):
    """Edit subscription type."""
    sub_type = SubscriptionType.query.get_or_404(id)

    if request.method == 'POST':
        sub_type.name = request.form.get('name', '').strip()
        sub_type.description = request.form.get('description', '').strip()

        db.session.commit()

        flash('Subscription type updated successfully.', 'success')
        return redirect(url_for('admin.subscription_types'))

    return render_template('admin/subscription_type_form.html', sub_type=sub_type, mode='edit')


@admin_bp.route('/subscription-types/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subscription_type(id):
    """Delete subscription type."""
    sub_type = SubscriptionType.query.get_or_404(id)

    if sub_type.subscriptions.count() > 0:
        flash('Cannot delete: subscription type is in use.', 'danger')
        return redirect(url_for('admin.subscription_types'))

    name = sub_type.name
    db.session.delete(sub_type)
    db.session.commit()

    flash(f'Subscription type "{name}" deleted.', 'success')
    return redirect(url_for('admin.subscription_types'))


# ===== Users =====
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    """Toggle user admin status."""
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin access {status} for {user.email}.', 'success')
    return redirect(url_for('admin.users'))
