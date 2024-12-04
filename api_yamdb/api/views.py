from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Review
from .serializers import CommentSerializer, ReviewSerializer


class TitleViewSet(viewsets.ModelViewSet):
    # Тут добавляется к базе данных среднее значение оценки
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))

    pass


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
