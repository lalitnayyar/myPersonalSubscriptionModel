"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from app.config import config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(app.root_path), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.subscriptions import subscriptions_bp
    from app.routes.payments import payments_bp
    from app.routes.reports import reports_bp
    from app.routes.budget import budget_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.notifications import notifications_bp
    from app.routes.groups import groups_bp
    from app.routes.attachments import attachments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(attachments_bp)

    # User loader for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processors
    @app.context_processor
    def utility_processor():
        from app.models import Notification
        from flask_login import current_user

        def get_unread_notifications_count():
            if current_user.is_authenticated:
                return Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()
            return 0

        return dict(
            unread_notifications_count=get_unread_notifications_count,
            supported_currencies=app.config['SUPPORTED_CURRENCIES']
        )

    # Initialize scheduler for notifications
    with app.app_context():
        from app.services.scheduler_service import init_scheduler
        init_scheduler(app)

    return app
