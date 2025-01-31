from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    CustomTokenObtainPairView,
    UserMeView,
    UserViewSet,
    sign_up_view,
)

v1_router = DefaultRouter()
v1_router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("api/v1/", include(v1_router.urls)),
    path("auth/signup/", sign_up_view, name="signup"),
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token"),
    path("users/me/", UserMeView.as_view(), name="users_me"),
]
