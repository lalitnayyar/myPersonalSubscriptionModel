"""Scheduler service for automated tasks."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()


def init_scheduler(app):
    """Initialize the scheduler with the Flask app."""
    if scheduler.running:
        return

    # Add jobs
    from app.services.notification_service import NotificationService

    # Run daily notification checks at 8 AM
    scheduler.add_job(
        func=NotificationService.run_all_checks,
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_notification_check',
        name='Daily notification check',
        replace_existing=True
    )

    # Also run checks on startup (after a delay)
    scheduler.add_job(
        func=NotificationService.run_all_checks,
        trigger='date',
        id='startup_notification_check',
        name='Startup notification check',
        replace_existing=True
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
