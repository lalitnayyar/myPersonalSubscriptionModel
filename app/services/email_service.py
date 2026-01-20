"""Email service for sending notifications."""
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail


class EmailService:
    """Service for sending email notifications."""

    @staticmethod
    def send_email(to, subject, body, html=None):
        """Send an email."""
        try:
            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, str) else to,
                body=body,
                html=html
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f'Failed to send email: {e}')
            return False

    @staticmethod
    def send_renewal_reminder(user, subscription):
        """Send renewal reminder email."""
        subject = f'Subscription Renewal Reminder: {subscription.name}'

        body = f"""
Hello {user.full_name},

This is a reminder that your subscription to {subscription.name} is due for renewal.

Details:
- Subscription: {subscription.name}
- Amount: {subscription.currency} {subscription.amount}
- Renewal Date: {subscription.next_renewal_date.strftime('%B %d, %Y')}
- Billing Cycle: {subscription.billing_cycle.capitalize()}

Please ensure you have sufficient funds or take necessary action before the renewal date.

Best regards,
Subscription Manager
        """

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">Subscription Reminder</h1>
    </div>
    <div style="padding: 20px; background: #f8f9fa;">
        <p>Hello <strong>{user.full_name}</strong>,</p>
        <p>This is a reminder that your subscription is due for renewal.</p>

        <div style="background: white; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #667eea; margin-top: 0;">{subscription.name}</h3>
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 5px 0; color: #666;">Amount:</td>
                    <td style="padding: 5px 0; font-weight: bold;">{subscription.currency} {subscription.amount}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #666;">Renewal Date:</td>
                    <td style="padding: 5px 0; font-weight: bold;">{subscription.next_renewal_date.strftime('%B %d, %Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #666;">Billing Cycle:</td>
                    <td style="padding: 5px 0;">{subscription.billing_cycle.capitalize()}</td>
                </tr>
            </table>
        </div>

        <p style="color: #666; font-size: 14px;">
            Please ensure you have sufficient funds or take necessary action before the renewal date.
        </p>
    </div>
    <div style="background: #333; color: #999; padding: 15px; text-align: center; font-size: 12px;">
        Subscription Manager - Your personal subscription tracker
    </div>
</body>
</html>
        """

        return EmailService.send_email(user.email, subject, body, html)

    @staticmethod
    def send_trial_ending_reminder(user, subscription):
        """Send trial ending reminder email."""
        days_left = (subscription.trial_end_date - subscription.trial_end_date.today()).days
        subject = f'Trial Ending Soon: {subscription.name}'

        body = f"""
Hello {user.full_name},

Your free trial for {subscription.name} is ending soon!

Details:
- Subscription: {subscription.name}
- Trial Ends: {subscription.trial_end_date.strftime('%B %d, %Y')}
- Days Remaining: {days_left}

After the trial ends, you'll be charged {subscription.currency} {subscription.amount} per {subscription.billing_cycle}.

Best regards,
Subscription Manager
        """

        return EmailService.send_email(user.email, subject, body)

    @staticmethod
    def send_payment_method_expiring(user, payment_method):
        """Send payment method expiring reminder."""
        subject = f'Payment Method Expiring: {payment_method.name}'

        body = f"""
Hello {user.full_name},

Your payment method is expiring soon.

Details:
- Payment Method: {payment_method.name}
- Last 4 Digits: {payment_method.last_four_digits}
- Expiry Date: {payment_method.expiry_date.strftime('%B %Y')}

Please update your payment method to avoid service interruptions.

Best regards,
Subscription Manager
        """

        return EmailService.send_email(user.email, subject, body)
