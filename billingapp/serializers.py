"""Serializers for the billing application."""

from rest_framework import serializers
from .models import User, Plan, Subscription, Invoice


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Handles password write-only logic and user creation
    with proper password hashing.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        """Meta information for the UserSerializer."""

        model = User
        fields = "__all__"

    def create(self, validated_data):
        """
        Create a new user instance with a hashed password.

        Args:
            validated_data (dict): Validated data from the request.

        Returns:
            User: The created user instance.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the Plan model.

    Serializes all fields of the plan.
    """

    class Meta:
        """Meta information for the PlanSerializer."""

        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model.

    Automatically sets read-only fields for user and timestamps.
    """

    class Meta:
        """Meta information for the SubscriptionSerializer."""

        model = Subscription
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Invoice model.

    Serializes all fields of the invoice.
    """

    class Meta:
        """Meta information for the InvoiceSerializer."""

        model = Invoice
        fields = "__all__"
