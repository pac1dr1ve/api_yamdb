# from rest_framework import permissions
#
#
# class IsAdminOrSuperuserPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and (request.user.is_authenticated and
#                                  (request.user.is_admin or request.user.is_superuser))
