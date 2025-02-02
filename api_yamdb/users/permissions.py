from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminUserOrSuperuser(BasePermission):
    """Позволяет доступ только администраторам и суперпользователям."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
