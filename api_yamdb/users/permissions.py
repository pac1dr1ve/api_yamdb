from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение, позволяющее редактировать
    объект только его владельцам.
    """

    def has_object_permission(self, request, view, obj):
        # Запрос на чтение разрешены для любого запроса,
        # поэтому мы всегда будем разрешать запросы GET, HEAD или OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Права на запись предоставляем только владельцу фрагмента.
        return obj == request.user
