"""Reports and analytics routes."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from app.models import Subscription, Category, Provider, PaymentMethod
from app.services.currency_service import CurrencyService
import csv
import io

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    """Reports overview page."""
    return render_template('reports/index.html')


@reports_bp.route('/reports/by-category')
@login_required
def by_category():
    """Report: Subscriptions by category."""
    categories = Category.query.all()
    currency = current_user.default_currency

    report_data = []
    for category in categories:
        subs = current_user.subscriptions.filter_by(
            category_id=category.id,
            status='active'
        ).all()

        if subs:
            monthly_total = sum(s.get_monthly_amount(currency) for s in subs)
            yearly_total = monthly_total * 12
            report_data.append({
                'category': category,
                'subscriptions': subs,
                'count': len(subs),
                'monthly_total': monthly_total,
                'yearly_total': yearly_total
            })

    # Uncategorized
    uncategorized = current_user.subscriptions.filter_by(
        category_id=None,
        status='active'
    ).all()
    if uncategorized:
        monthly_total = sum(s.get_monthly_amount(currency) for s in uncategorized)
        report_data.append({
            'category': None,
            'subscriptions': uncategorized,
            'count': len(uncategorized),
            'monthly_total': monthly_total,
            'yearly_total': monthly_total * 12
        })

    # Sort by monthly total
    report_data.sort(key=lambda x: x['monthly_total'], reverse=True)

    total_monthly = sum(d['monthly_total'] for d in report_data)
    total_yearly = total_monthly * 12

    return render_template('reports/by_category.html',
                           report_data=report_data,
                           total_monthly=total_monthly,
                           total_yearly=total_yearly,
                           currency=currency)


@reports_bp.route('/reports/by-provider')
@login_required
def by_provider():
    """Report: Subscriptions by provider."""
    providers = Provider.query.all()
    currency = current_user.default_currency

    report_data = []
    for provider in providers:
        subs = current_user.subscriptions.filter_by(
            provider_id=provider.id,
            status='active'
        ).all()

        if subs:
            monthly_total = sum(s.get_monthly_amount(currency) for s in subs)
            report_data.append({
                'provider': provider,
                'subscriptions': subs,
                'count': len(subs),
                'monthly_total': monthly_total,
                'yearly_total': monthly_total * 12
            })

    # No provider
    no_provider = current_user.subscriptions.filter_by(
        provider_id=None,
        status='active'
    ).all()
    if no_provider:
        monthly_total = sum(s.get_monthly_amount(currency) for s in no_provider)
        report_data.append({
            'provider': None,
            'subscriptions': no_provider,
            'count': len(no_provider),
            'monthly_total': monthly_total,
            'yearly_total': monthly_total * 12
        })

    report_data.sort(key=lambda x: x['monthly_total'], reverse=True)

    total_monthly = sum(d['monthly_total'] for d in report_data)
    total_yearly = total_monthly * 12

    return render_template('reports/by_provider.html',
                           report_data=report_data,
                           total_monthly=total_monthly,
                           total_yearly=total_yearly,
                           currency=currency)


@reports_bp.route('/reports/by-payment-method')
@login_required
def by_payment_method():
    """Report: Subscriptions by payment method."""
    payment_methods = current_user.payment_methods.all()
    currency = current_user.default_currency

    report_data = []
    for pm in payment_methods:
        subs = pm.subscriptions.filter_by(
            user_id=current_user.id,
            status='active'
        ).all()

        if subs:
            monthly_total = sum(s.get_monthly_amount(currency) for s in subs)
            report_data.append({
                'payment_method': pm,
                'subscriptions': subs,
                'count': len(subs),
                'monthly_total': monthly_total,
                'yearly_total': monthly_total * 12
            })

    # No payment method
    no_pm = current_user.subscriptions.filter_by(
        payment_method_id=None,
        status='active'
    ).all()
    if no_pm:
        monthly_total = sum(s.get_monthly_amount(currency) for s in no_pm)
        report_data.append({
            'payment_method': None,
            'subscriptions': no_pm,
            'count': len(no_pm),
            'monthly_total': monthly_total,
            'yearly_total': monthly_total * 12
        })

    report_data.sort(key=lambda x: x['monthly_total'], reverse=True)

    total_monthly = sum(d['monthly_total'] for d in report_data)
    total_yearly = total_monthly * 12

    return render_template('reports/by_payment_method.html',
                           report_data=report_data,
                           total_monthly=total_monthly,
                           total_yearly=total_yearly,
                           currency=currency)


@reports_bp.route('/reports/by-status')
@login_required
def by_status():
    """Report: Subscriptions by status."""
    currency = current_user.default_currency

    statuses = ['active', 'inactive', 'cancelled']
    report_data = []

    for status in statuses:
        subs = current_user.subscriptions.filter_by(status=status).all()
        if subs:
            monthly_total = sum(s.get_monthly_amount(currency) for s in subs)
            report_data.append({
                'status': status,
                'subscriptions': subs,
                'count': len(subs),
                'monthly_total': monthly_total,
                'yearly_total': monthly_total * 12
            })

    total_monthly = sum(d['monthly_total'] for d in report_data)
    total_yearly = total_monthly * 12

    return render_template('reports/by_status.html',
                           report_data=report_data,
                           total_monthly=total_monthly,
                           total_yearly=total_yearly,
                           currency=currency)


@reports_bp.route('/reports/export/csv')
@login_required
def export_csv():
    """Export subscriptions to CSV."""
    subscriptions = current_user.subscriptions.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Name', 'Provider', 'Category', 'Amount', 'Currency',
        'Billing Cycle', 'Status', 'Next Renewal', 'Start Date',
        'Auto Renew', 'Is Trial', 'Notes'
    ])

    for sub in subscriptions:
        writer.writerow([
            sub.name,
            sub.provider.name if sub.provider else '',
            sub.category.name if sub.category else '',
            sub.amount,
            sub.currency,
            sub.billing_cycle,
            sub.status,
            sub.next_renewal_date.strftime('%Y-%m-%d') if sub.next_renewal_date else '',
            sub.start_date.strftime('%Y-%m-%d'),
            'Yes' if sub.auto_renew else 'No',
            'Yes' if sub.is_trial else 'No',
            sub.notes or ''
        ])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=subscriptions_{datetime.now().strftime("%Y%m%d")}.csv'}
    )


@reports_bp.route('/reports/spending-trends')
@login_required
def spending_trends():
    """Report: Spending trends over time."""
    currency = current_user.default_currency

    # Get monthly data for last 12 months
    today = datetime.utcnow().date()
    months_data = []

    for i in range(11, -1, -1):
        month_date = today - timedelta(days=i * 30)
        month_label = month_date.strftime('%b %Y')

        # For simplicity, we'll use current monthly spend
        # In a real app, you'd track historical spending
        monthly_spend = current_user.get_monthly_spend(currency)

        months_data.append({
            'label': month_label,
            'amount': monthly_spend
        })

    return render_template('reports/spending_trends.html',
                           months_data=months_data,
                           currency=currency)
