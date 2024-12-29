import random
import re
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, viewsets, permissions, generics, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, Enum
from users.serializers import (
    UserSerializer,
    UserTokenSerializer,
    SignUpSerializer,
)


class SignUpView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):

        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # role = serializer.validated_data.pop("role", "user")
        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]

        existing_user_email = User.objects.filter(email=email).first()
        existing_user_username = User.objects.filter(username=username).first()

        confirmation_code = self.create_confirmation_code()

        # Если username и email существуют, отправляем confirmation_code
        if existing_user_email and existing_user_username:
            # Обновляем код подтверждения и отправляем его повторно
            existing_user_email.confirmation_code = confirmation_code
            existing_user_email.save()

            self.send_confirmation_email(existing_user_email, confirmation_code)

            return Response(serializer.data)
        # Если email существует (username уникален)
        if existing_user_email:
            return Response(
                {"detail": "Пользователь с таким email уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Если username существует (email уникален)
        if existing_user_username:
            return Response(
                {"detail": "Пользователь с таким username уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Если username и email уникальны
        # Создание нового пользователя
        user = User.objects.create_user(
            username=username, email=email, role=Enum.USER
        )

        user.confirmation_code = confirmation_code
        user.save()
        # Отправляем код подтверждения на email
        self.send_confirmation_email(user, confirmation_code)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            user.is_active = False
            user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_confirmation_email(user, confirmation_code):
        send_mail(
            "Код подтверждения",
            f"Ваш код подтверждения: {confirmation_code}",
            "yamdb@example.com",
            [user.email],
            fail_silently=False,
        )
        return user

    @staticmethod
    def create_confirmation_code():
        confirmation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5),
        )
        return confirmation_code


class UserMeView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request):
        username = request.data.get('username', None)
        role = request.data.get('role', None)  # Добавляем получение роли пользователя

        if username:
            if not re.match(r"^[\w.@+-]+\Z", username):
                return Response({"error": "Никнейм содержит недопустимы символы!"},
                                status=status.HTTP_400_BAD_REQUEST)

        if role:
            return Response({"error": "Изменение роли пользователя недопустимо!"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['user_delete', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    # @action(detail=True, methods=['get'])
    # def user_detail(self, request, **kwargs):
    #     user = self.get_object()
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def update(self, request, *args, **kwargs):
    #     user = get_object_or_404(User, username=self.kwargs["username"])
    #     serializer = ChangePasswordSerializer(data=request.data)
    #
    #     if serializer.is_valid():
    #         if not user.check_password(serializer.validated_data["old_password"]):
    #             return Response({"old_password": ["Неправильный пароль."]}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         user.set_password(serializer.validated_data["new_password"])
    #         user.save()
    #         return Response({
    #             "status": "success",
    #             "code": status.HTTP_200_OK,
    #             "message": "Пароль обновлен успешно",
    #             "data": [],
    #         }, status=status.HTTP_200_OK)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=['put'])
    # def user_update(self, request, **kwargs):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(detail=False, methods=['delete'])
    # def user_delete(self, request, username):
    #
    #     if not request.user.is_staff:
    #         return Response("Удачно", status=status.HTTP_204_NO_CONTENT)
    #     try:
    #         user = User.objects.get(username=username)
    #         user.delete()
    #         return Response("Пользователь успешно удален", status=status.HTTP_204_NO_CONTENT)
    #     except User.DoesNotExist:
    #         return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get("search")
        if username is not None:
            queryset = queryset.filter(username=username).distinct()
        return queryset

    # @action(detail=True, methods=['get', 'patch', 'delete'])
    # def user(self, request, username=None):
    #     user = User.objects.filter(username=username).first()
    #     if not user:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    #     if request.method == 'GET':
    #         serializer = self.get_serializer(user)
    #         # return Response(serializer.data)
    #         return Response(status=status.HTTP_200_OK)
    #
    #     elif request.method == 'PATCH':
    #         serializer = self.get_serializer(user, data=request.data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)
    #
    #     elif request.method == 'DELETE':
    #         user.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(username=serializer.validated_data.get("username"))
            token = RefreshToken.for_user(user)
            data = {
                "token": str(token.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)

        except TokenError as e:
            raise InvalidToken(e.args[0])

        except User.DoesNotExist:
            return Response("Пользователь не найден",
                            status=status.HTTP_404_NOT_FOUND)
