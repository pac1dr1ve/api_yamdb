from rest_framework import permissions


class CustomIsAdminUserOrSuperuser(permissions.BasePermission):
    """
    Позволяет доступ только администраторам и суперпользователям
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser) \
               or bool(request.user and request.user.is_staff)
