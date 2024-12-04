from rest_framework import mixins, viewsets, filters

from .permissions import AdminOrReadOnly


class CategoryAndGenreMixin(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminOrReadOnly,)
