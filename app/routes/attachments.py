"""Attachment routes for subscription documents."""
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Subscription, SubscriptionAttachment

attachments_bp = Blueprint('attachments', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@attachments_bp.route('/subscriptions/<int:sub_id>/attachments')
@login_required
def index(sub_id):
    """List all attachments for a subscription."""
    subscription = Subscription.query.filter_by(
        id=sub_id, user_id=current_user.id
    ).first_or_404()

    attachments = subscription.attachments.order_by(
        SubscriptionAttachment.uploaded_at.desc()
    ).all()

    return render_template('attachments/index.html',
                           subscription=subscription,
                           attachments=attachments)


@attachments_bp.route('/subscriptions/<int:sub_id>/attachments/upload', methods=['GET', 'POST'])
@login_required
def upload(sub_id):
    """Upload attachment for subscription."""
    subscription = Subscription.query.filter_by(
        id=sub_id, user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('attachments.upload', sub_id=sub_id))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('attachments.upload', sub_id=sub_id))

        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f'{uuid.uuid4()}.{ext}'

            # Create attachments directory if not exists
            attachments_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'attachments',
                str(subscription.id)
            )
            os.makedirs(attachments_dir, exist_ok=True)

            # Save file
            filepath = os.path.join(attachments_dir, unique_filename)
            file.save(filepath)

            # Get file size
            file_size = os.path.getsize(filepath)

            # Get file type from form
            file_type = request.form.get('file_type', 'other')
            notes = request.form.get('notes', '').strip()

            # Create attachment record
            attachment = SubscriptionAttachment(
                subscription_id=subscription.id,
                filename=unique_filename,
                original_filename=original_filename,
                file_type=file_type,
                file_size=file_size,
                notes=notes
            )
            db.session.add(attachment)
            db.session.commit()

            flash('File uploaded successfully.', 'success')
            return redirect(url_for('subscriptions.view', id=sub_id))

        flash('File type not allowed.', 'danger')
        return redirect(url_for('attachments.upload', sub_id=sub_id))

    return render_template('attachments/upload.html', subscription=subscription)


@attachments_bp.route('/attachments/<int:id>/download')
@login_required
def download(id):
    """Download attachment."""
    attachment = SubscriptionAttachment.query.get_or_404(id)

    # Verify ownership
    subscription = Subscription.query.filter_by(
        id=attachment.subscription_id,
        user_id=current_user.id
    ).first_or_404()

    attachments_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'attachments',
        str(subscription.id)
    )

    return send_from_directory(
        attachments_dir,
        attachment.filename,
        as_attachment=True,
        download_name=attachment.original_filename
    )


@attachments_bp.route('/attachments/<int:id>/view')
@login_required
def view(id):
    """View attachment (for images and PDFs)."""
    attachment = SubscriptionAttachment.query.get_or_404(id)

    # Verify ownership
    subscription = Subscription.query.filter_by(
        id=attachment.subscription_id,
        user_id=current_user.id
    ).first_or_404()

    attachments_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'attachments',
        str(subscription.id)
    )

    return send_from_directory(attachments_dir, attachment.filename)


@attachments_bp.route('/attachments/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete attachment."""
    attachment = SubscriptionAttachment.query.get_or_404(id)

    # Verify ownership
    subscription = Subscription.query.filter_by(
        id=attachment.subscription_id,
        user_id=current_user.id
    ).first_or_404()

    # Delete file
    attachments_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'attachments',
        str(subscription.id)
    )
    filepath = os.path.join(attachments_dir, attachment.filename)

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass

    # Delete record
    db.session.delete(attachment)
    db.session.commit()

    flash('Attachment deleted.', 'success')
    return redirect(url_for('subscriptions.view', id=subscription.id))
