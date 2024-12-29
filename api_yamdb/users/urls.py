from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomTokenObtainPairView, UserMeView, UserViewSet, SignUpView

# v1_router.register('users', UserViewSet, basename='users')
# urlpatterns = [
#     path("auth/signup/", UserViewSet.as_view({"post": "create"}), name="auth_signup"),
#     path("auth/token/", CustomTokenObtainPairView.as_view()),
#     path("users/me/", UserMeView.as_view(), name="users_me"),
#     path("users/<str:username>/", UserViewSet.as_view({"get": "retrieve",
#                                                        "delete": "destroy"}), name="user_detail"),
#     path("users/<int:pk>/", UserViewSet.as_view({"get": "retrieve",
#                                                  "delete": "destroy"}), name="user"),
#     path("users/set_password/", UserViewSet.as_view({"post": "update"}), name="user_update"),
#     path("users/current_user/", UserMeView.as_view(), name="current_user"),
# ]
v1_router = DefaultRouter()
urlpatterns = [
    path("api/v1/", include(v1_router.urls)),
    path("auth/signup/", SignUpView.as_view({"post": "create"}), name="signup"),
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token"),
    path("users/me/", UserMeView.as_view(), name="users_me"),
    path("users/<str:username>/", UserViewSet.as_view({"get": "retrieve",
                                                       "delete": "destroy"}), name="user_detail"),

]
