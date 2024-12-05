from rest_framework import mixins, viewsets, filters

from .permissions import IsAdminOrReadOnly


class CategoryAndGenreMixin(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
