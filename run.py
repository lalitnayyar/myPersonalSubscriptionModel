"""Application entry point."""
from app import create_app, db
from app.models import User, Subscription, Category, Provider, SubscriptionType, PaymentMethod, Notification

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make shell context for flask shell command."""
    return {
        'db': db,
        'User': User,
        'Subscription': Subscription,
        'Category': Category,
        'Provider': Provider,
        'SubscriptionType': SubscriptionType,
        'PaymentMethod': PaymentMethod,
        'Notification': Notification
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
