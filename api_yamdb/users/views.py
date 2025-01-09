import random
import string

from django.core.mail import send_mail
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Role, User
from users.permissions import CustomIsAdminUserOrSuperuser
from users.serializers import (
    SignUpSerializer,
    UserSerializer,
    UserTokenSerializer
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

        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]

        existing_user_email = User.objects.filter(email=email).first()
        existing_user_username = User.objects.filter(
            username=username).first()

        confirmation_code = self.create_confirmation_code()

        if existing_user_email and existing_user_username:
            existing_user_email.confirmation_code = confirmation_code
            existing_user_email.save()

            self.send_confirmation_email(
                existing_user_email, confirmation_code)

            return Response(serializer.data)

        if existing_user_email:
            return Response(
                {"detail": "Пользователь с таким email уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if existing_user_username:
            return Response(
                {"detail": "Пользователь с таким "
                           "username уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username, email=email,
            role=Role.USER.value,
        )
        user.confirmation_code = confirmation_code
        user.save()

        self.send_confirmation_email(user, confirmation_code)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
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


class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        username = request.data.get("username", None)

        if username and User.objects.filter(
                username=username).exclude(
                pk=request.user.pk).exists():
            return Response({"error": "Это username уже занято"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(request.user,
                                    data=request.data, partial=True)

        if serializer.is_valid():
            if ("role" in request.data
                    and request.data["role"] != request.user.role):
                return Response({"error": "Изменение роли "
                                          "для пользователя недопустимо!"},
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)

            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    search_fields = ("username",)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action in ["destroy", "retrieve",
                           "partial_update", "create", "list"]:
            self.permission_classes = [CustomIsAdminUserOrSuperuser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def check_password(self, user, old_password):
        """Проверка пароля на корректность."""
        if not user.check_password(old_password):
            return False
        return True

    def update_password(self, user, new_password):
        """Обновление пароля пользователя."""
        user.set_password(new_password)
        user.save()

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user,
                                         data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get("search")
        if username is not None:
            queryset = queryset.filter(username=username).distinct()
        return queryset


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(username=serializer.
                                    validated_data.get("username"))
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
