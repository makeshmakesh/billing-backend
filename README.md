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
- payment integration (Stripe).
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
- Stripe

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
POST `/plans/`  Create a plan , only staff access
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

### Payment

GET `/api/pay/` Opens payment page , enter invoice id and card details  
POST `/api/create-payment-intent/` Create stripe payment for the invoice  
POST `/api/payment-success/` Mark the invoice paid  


## Stripe Integration
Stripe payment integration is implemented using Stripe.js for card handling and Django backend for creating payment intents and confirming payments.

### Stripe Payment Flow

1. User enters the `invoice_id` and card details on the payment page (`/templates/payment.html`). Visit - `/api/pay/`
2. A POST request is sent to:
   - `/api/create-payment-intent/` – to create a Stripe PaymentIntent using the invoice amount.
3. Stripe processes the card, and on success:
   - A POST request is sent to `/api/payment-success/` with the `invoice_id`.
   - The invoice status is updated to `paid`.

Make sure to set your `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` in environment variables before starting the server.
We can store these key in aws ssm as well for better security and maintainability.

#### Test data for stripe

card number success - 4242 4242 4242 4242
card number declined - 4000 0000 0000 9995


## Bonus Functionality

* Reminder email (console print)
* Stripe integration
* Admin-only access to view all invoices/subscriptions
* Added query parm to filter using status for invoice and subscriptions
* Added automated tests in github actions
