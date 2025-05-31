"""THis module is used to define custom permissions"""

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Allow users to access their own subscriptions, and allow admins to access all.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
