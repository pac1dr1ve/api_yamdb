from django.urls import path

from .views import (UserMeView,
                    UserViewSet,
                    ObtainAuthToken)

urlpatterns = [
    path('auth/signup/', UserViewSet.as_view({'post': 'create'}),
         name='auth_signup'),
    path('auth/token/', ObtainAuthToken.as_view(), name='token_obtain_pair'),
    path('users/me/', UserMeView.as_view(), name='users_me'),
]
