"""This module is used to register the models in admin center"""
from django.contrib import admin
from .models import User, Plan, Subscription, Invoice


admin.site.register(User)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Invoice)
