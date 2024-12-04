from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('auth/signup/', UserViewSet.as_view({'post': 'create'}), name='auth_signup'),
    path('auth/token/', UserViewSet.as_view({'post': 'get_token'}), name='token_obtain_pair'),
    path('users/me/', UserViewSet.as_view({'patch': 'partial_update'}), name='users_me'),
]
