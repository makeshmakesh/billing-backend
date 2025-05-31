"""
URL routing for the billing app.

Includes:
- JWT auth (login & token refresh)
- User, Plan, Subscription, and Invoice viewsets
"""

from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserViewSet, PlanViewSet, SubscriptionViewSet, InvoiceViewSet

# Registering viewsets with DRF router
router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'subscription', SubscriptionViewSet, basename='subscription')
router.register(r'invoices', InvoiceViewSet, basename='invoice')

# JWT token endpoints for login and refresh
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # refresh token
]

# Include all router-generated URLs
urlpatterns += router.urls
