"""
Celery tasks for managing the billing lifecycle:
- Invoice generation
- Overdue status updates
- Reminder notifications
"""
#pylint:disable=E1101
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from .models import Subscription, Invoice


@shared_task
def generate_daily_invoices():
    """
    Generate invoices for all active subscriptions
    whose start_date is today.

    Ensures that invoices are not duplicated
    if the task runs more than once per day.
    """
    today = now().date()
    active_subs = Subscription.objects.filter(start_date=today, status="active")

    for sub in active_subs:
        # Avoid duplicate invoices
        invoice_exists = Invoice.objects.filter(
            subscription=sub, issue_date=today
        ).exists()

        if invoice_exists:
            continue

        # Create new invoice
        Invoice.objects.create(
            user=sub.user,
            plan=sub.plan,
            subscription=sub,
            amount=sub.plan.price,
            issue_date=today,
            due_date=today + timedelta(days=7),
            status="pending",
        )


@shared_task
def mark_overdue_invoices():
    """
    Mark all pending invoices as 'overdue' if their due_date has passed.

    Returns:
        str: A summary of how many invoices were updated.
    """
    today = now().date()
    overdue_invoices = Invoice.objects.filter(status="pending", due_date__lt=today)
    count = overdue_invoices.update(status="overdue")
    return f"{count} invoices marked as overdue."


@shared_task
def send_pending_invoice_reminders():
    """
    Send reminder notifications (via print/log) for all
    pending invoices that are not yet due.

    Returns:
        str: A summary of how many reminders were sent.
    """
    today = now().date()
    pending_invoices = Invoice.objects.filter(status="pending", due_date__gte=today)

    for invoice in pending_invoices:
        print(
            f"[REMINDER] Invoice #{invoice.id} for user "
            f"{invoice.user.username} is still pending. Due on {invoice.due_date}."
        )

    return f"{pending_invoices.count()} reminders sent."
