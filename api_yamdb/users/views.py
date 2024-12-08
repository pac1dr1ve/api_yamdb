import random
import string
from django.core.mail import send_mail
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdminOrSuperuserPermission
from .serializers import (UserSerializer,
                          UserRegistrationSerializer,
                          UserTokenSerializer, ChangePasswordSerializer)


class UserMeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user,
                                    data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrSuperuserPermission)
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # Проверка на существование пользователя с таким же email или username
        if User.objects.filter(email=email).exists() or User.objects.filter(
                username=username).exists():
            return Response({'detail': 'Пользователь с таким email '
                                       'или username уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)

        confirmation_code = ''.join(random.choices(string.ascii_uppercase
                                                   + string.digits,
                                                   k=50))

        user = User.objects.create_user(username=username, email=email)

        user.confirmation_code = confirmation_code
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"old_password": ["Неправильный пароль."]},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {'status': 'success', 'code': status.HTTP_200_OK, 'message':
                    'Пароль обновлен успешно', 'data': []})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_confirmation_email(user, confirmation_code=None):
        send_mail('Код подтверждения',
                  f'Ваш код подтверждения: {confirmation_code}',
                  'yamdb@example.com',
                  [user.email],
                  fail_silently=False)

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response("Unauthorized",
                        status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.is_admin or request.user.is_superuser:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get('search')
        if username is not None:
            queryset = queryset.filter(username__icontains=username)
        return queryset


class ObtainAuthToken(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh),
                             'access': str(refresh.access_token)},
                            status=status.HTTP_200_OK)
