from django.urls import path

from .views import UserViewSet, ObtainAuthToken, UserMeView

urlpatterns = [
    path('auth/signup/', UserViewSet.as_view({'post': 'create'}), name='auth_signup'),
    path('auth/token/', ObtainAuthToken.as_view(), name='token_obtain'),
    path('users/me/', UserMeView.as_view(), name='users_me'),
    path('users/<str:username>/', UserViewSet.as_view({'get': 'retrieve',
                                                       'delete': 'destroy'}), name='user_detail'),

    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve',
                                                 'delete': 'destroy'}), name='user'),
    path('users/set_password/', UserViewSet.as_view({'post': 'update'}), name='user_update'),
    path('users/current_user/', UserMeView.as_view(), name='current_user'),
]
