"""This file defines the Django app configuration"""
from django.apps import AppConfig


class BillingappConfig(AppConfig):
    """App configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billingapp'
