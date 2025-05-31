"""
ViewSets for User, Plan, Subscription, and Invoice models.
Handles CRUD operations, custom actions (unsubscribe, pay), and permission logic.
"""

# pylint:disable=E1101,W0613, W0718
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db import DatabaseError

from .models import User, Plan, Subscription, Invoice
from .serializers import (
    UserSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    InvoiceSerializer,
)
from .permissions import IsAdminUser, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and retrieving users.
    Anyone can register; other actions require authentication.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Allow registration without authentication, protect other actions."""
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]


class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subscription plans.
    Only accessible by admin users.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "put", "patch", "delete"]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user subscriptions.
    Users can subscribe, view their own, or cancel.
    Admin can view all.
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Return subscriptions:
        - All if admin
        - Only user's own if regular user
        - Filter by `status` if provided
        """
        user = self.request.user
        queryset = (
            Subscription.objects.all()
            if user.is_staff
            else Subscription.objects.filter(user=user)
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def perform_create(self, serializer):
        """
        Ensure user can only have one active subscription.
        """
        try:
            active_subscription = Subscription.objects.filter(
                user=self.request.user, status="active"
            ).exists()

            if active_subscription:
                raise serializers.ValidationError(
                    "You already have an active subscription."
                )

            serializer.save(user=self.request.user)

        except DatabaseError as db_err:
            raise serializers.ValidationError(f"Database error occurred: {str(db_err)}")

    def destroy(self, request, *args, **kwargs):
        """
        Override default delete to soft-cancel the subscription.
        """
        try:
            instance = self.get_object()
            if instance.status == "cancelled":
                return Response(
                    {"detail": "Subscription already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.status = "cancelled"
            instance.save()
            return Response(
                {"detail": "Subscription cancelled."}, status=status.HTTP_200_OK
            )
        except Exception as ex:
            return Response(
                {"detail": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request, pk=None):
        """
        Custom action to cancel subscription via /subscription/{id}/unsubscribe/
        """
        try:
            subscription = self.get_object()

            if subscription.status == "cancelled":
                return Response(
                    {"detail": "Subscription already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription.status = "cancelled"
            subscription.save()

            return Response(
                {"detail": "Subscription cancelled successfully."},
                status=status.HTTP_200_OK,
            )
        except Subscription.DoesNotExist:
            return Response(
                {"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"detail": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing invoices.
    Users can view/pay their own invoices.
    Admins can view all.
    """

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return invoices for the current user.
        Admins can view all invoices.
        Can filter by `status`.
        """
        user = self.request.user
        queryset = (
            Invoice.objects.all()
            if user.is_staff
            else Invoice.objects.filter(user=user)
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    @action(detail=True, methods=["post"], url_path="pay")
    def pay_invoice(self, request, pk=None):
        """
        Custom action to pay an invoice via /invoices/{id}/pay/
        Mock payment flow only.
        """
        try:
            invoice = self.get_object()

            if invoice.status == "paid":
                return Response(
                    {"detail": "Invoice already paid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mock payment
            print(f"Mock payment for Invoice #{invoice.id}, amount: {invoice.amount}")

            invoice.status = "paid"
            invoice.save()

            return Response(
                {"detail": "Payment successful."}, status=status.HTTP_200_OK
            )

        except Invoice.DoesNotExist:
            return Response(
                {"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"detail": "A database error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as ex:
            return Response(
                {"detail": f"Unexpected error: {str(ex)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
