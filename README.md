# 💳 Billing Backend System

This is a backend system built with Django and Celery to handle user subscriptions, billing plans, invoice generation, and basic billing lifecycle management for SaaS applications.

---

## 🚀 Features

- User sign-up and subscription management.
- Predefined plans: **Basic**, **Pro**, **Enterprise**.
- Daily invoice generation using **Celery**.
- Invoice lifecycle tracking: `pending`, `paid`, `overdue`.
- Admin-only access for managing plans.
- API endpoints for subscription and invoice payment.
- Mock payment integration (Stripe-like).
- Periodic tasks for:
  - Generating invoices.
  - Marking overdue invoices.
  - Sending reminders (print-based).

---

## 🛠 Tech Stack

- Python 3.12+
- Django 4.x
- Django REST Framework
- Celery
- Redis (as broker)
- SQLite or Postgres
- Stripe (mocked)

---

## 📦 Setup Instructions

### Run the below commands

```bash
git clone git@github.com:makeshmakesh/billing-backend.git
cd billing-backend
virtualenv venv
. ./venv/bin/activate
pip install -r requirements.txt
cd billingapi
python3 manage.py makemigration
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

#### Optional (if need to test celery)
```
sudo apt-get install redis-server
celery -A billingapi worker --loglevel=info
```

## Run Tasks Manually
#### Generate Invoices
```
python3 manage.py shell

from billingapp.tasks import generate_daily_invoices
generate_daily_invoices.delay()
```
#### Mark Overdue Invoices
```
python3 manage.py shell

from billingapp.tasks import mark_overdue_invoices
mark_overdue_invoices.delay()
```

#### Send Reminder for Unpaid Invoices

```
python3 manage.py shell

from billingapp.tasks import send_pending_invoice_reminders
send_pending_invoice_reminders.delay()
```

## Staff Access
Only staff (is_staff=True) can:

* Create, update, delete billing plans
* View all subscriptions and invoices


## API Endpoints Summary

### User

POST `/api/users/`

### Auth
POST `/api/token/` – Login and get JWT
POST `/api/token/refresh/` – Refresh token

### Plans (staff Only)
GET `/plans/` All autheniticated user
POST `/plans/`
PUT `/plans/{id}/`
DELETE `/plans/{id}/`

### Subscriptions

For staff it will list all subscriptions, for other users it will list only theirs
GET `/subscriptions/` - Supports ?status=active|cancelled|expired
POST `/subscriptions/`
POST `/subscriptions/{id}/unsubscribe/`

### Invoices
For staff it will list all invoices, for other users it will list only theirs
GET `/invoices/` – Supports ?status=pending|paid|overdue
POST `/invoices/{id}/pay/`

## Stripe Integration (Mock) - TO-DO Real stripe
Stripe integration is mocked using a simple print statement in the payment endpoint. I will implement later.

## Bonus Functionality

* Reminder email (console print)
* Stripe integration — mocked via a print statement
* Admin-only access to view all invoices/subscriptions
* Added query parm to filter using status for invoice and subscriptions
