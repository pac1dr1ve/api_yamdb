from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet,
    sign_up_view,
    get_token_obtain_pair_view,
)

v1_router = DefaultRouter()
v1_router.register(r"users", UserViewSet, basename="user")

auth_urlpatterns = [
    path("signup/", sign_up_view, name="signup"),
    path("token/", get_token_obtain_pair_view, name="token"),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
]
