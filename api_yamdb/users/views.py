import random
import string
from django.core.mail import send_mail
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ChangePasswordSerializer, UserTokenSerializer,
)


class UserMeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return Response("Незарегистрированный пользователь",
        #                     status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.pop("role", "user")
        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]

        existing_user_email = User.objects.filter(email=email).first()
        existing_user_username = User.objects.filter(username=username).first()

        confirmation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5),
        )

        # Если username и email существуют, отправляем confirmation_code
        if existing_user_email and existing_user_username:
            # Обновляем код подтверждения и отправляем его повторно
            existing_user_email.confirmation_code = confirmation_code
            existing_user_email.save()
            self.send_confirmation_email(existing_user_email, confirmation_code)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

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
            username=username, email=email, role=role,
        )

        user.confirmation_code = confirmation_code
        user.save()
        # Отправляем код подтверждения на email
        self.send_confirmation_email(user, confirmation_code)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": ["Неправильный пароль."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Пароль обновлен успешно",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )
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

    @action(detail=False, methods=["get"])
    def current_user(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False)
    def user_delete(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.user.is_admin or request.user.is_superuser:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get("search")
        if username is not None:
            queryset = queryset.filter(username__icontains=username).distinct()
        return queryset


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
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден",
                                              code=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)
