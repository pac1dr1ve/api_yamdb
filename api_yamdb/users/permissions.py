from rest_framework.permissions import BasePermission


class CustomIsAdminUserOrSuperuser(BasePermission):
    """
    Позволяет доступ только администраторам и суперпользователям.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin
