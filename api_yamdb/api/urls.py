from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet,
    sign_up_view,
    get_token_obtain_pair_view,
)
from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet
)

v1_router = DefaultRouter()
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

v1_router.register('users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')

auth_urlpatterns = [
    path('signup/', sign_up_view, name='signup'),
    path('token/', get_token_obtain_pair_view, name='token'),
]
urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('', include(v1_router.urls)),
]
