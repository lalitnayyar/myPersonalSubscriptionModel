"""Scheduler service for automated tasks."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()
_app = None


def run_notification_checks():
    """Run notification checks within app context."""
    global _app
    if _app is None:
        return

    with _app.app_context():
        from app.services.notification_service import NotificationService
        try:
            NotificationService.run_all_checks()
        except Exception as e:
            _app.logger.error(f'Error running notification checks: {e}')


def init_scheduler(app):
    """Initialize the scheduler with the Flask app."""
    global _app
    _app = app

    if scheduler.running:
        return

    # Run daily notification checks at 8 AM
    scheduler.add_job(
        func=run_notification_checks,
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_notification_check',
        name='Daily notification check',
        replace_existing=True
    )

    # Also run checks on startup (after a short delay to let app fully initialize)
    scheduler.add_job(
        func=run_notification_checks,
        trigger='date',
        run_date=None,  # Run immediately
        id='startup_notification_check',
        name='Startup notification check',
        replace_existing=True,
        misfire_grace_time=60
    )

    try:
        scheduler.start()
        app.logger.info('Scheduler started successfully')
    except Exception as e:
        app.logger.error(f'Failed to start scheduler: {e}')


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
