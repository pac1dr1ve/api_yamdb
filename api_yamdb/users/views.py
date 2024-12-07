from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    def create(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not all(username, email, password):
            return Response({"detail": "Требуется имя пользователя, "
                                       "адрес электронной почты и пароль"},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # if ('username' not in request.data or 'email'
        #         not in request.data or 'password' not in request.data):
        #     return Response({"detail": "Требуется имя пользователя, "
        #                                "адрес электронной почты и пароль"},
        #                     status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_token(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not all([username, confirmation_code]):
            return Response({"detail": "Требуется имя пользователя "
                                       "и код подтверждения"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    def partial_update(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        if 'role' in request.data:
            del request.data['role']
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
