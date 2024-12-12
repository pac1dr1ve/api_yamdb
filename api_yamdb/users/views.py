import random
import string
from django.core.mail import send_mail
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    UserTokenSerializer,
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
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEndpointTestCase(APITestCase):
    def test_unauthorized_access(self):
        # Незарегистрированным пользователям не доступен эндпоинт api/v1/users/
        url = reverse('api:v1:users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Пользователям без роли admin или superuser не доступен эндпоинт api/v1/users/{username}/
        user = UserViewSet

        url_with_username = reverse()
        self.client.force_authenticate(user=user)
        response_with_username = self.client.get(url_with_username)
        self.assertEqual(response_with_username.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_access(self):
        moderator = User.objects.create_user(role='moderator')
        url_moderator = reverse('api:v1:users')
        self.client.force_authenticate(user=moderator)
        response_moderator = self.client.get(url_moderator)
        self.assertEqual(response_moderator.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.pop("role", "user")
        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]

        existing_user_email = User.objects.filter(email=email).first()
        existing_user_username = User.objects.filter(username=username).first()

        if existing_user_email:
            # Обновляем код подтверждения и отправляем его повторно
            confirmation_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=50),
            )
            existing_user_email.confirmation_code = confirmation_code
            existing_user_email.save()

            self.send_confirmation_email(existing_user_email, confirmation_code)
            return Response(
                {"detail": "Код подтверждения отправлен повторно."},
                status=status.HTTP_200_OK,
            )

        if existing_user_username:
            return Response(
                {"detail": "Пользователь с таким username уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создание нового пользователя
        user = User.objects.create_user(
            username=username, email=email, role=role,
        )
        user.set_unusable_password()
        confirmation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=50),
        )
        user.confirmation_code = confirmation_code
        user.save()

        # Отправляем код подтверждения на email
        self.send_confirmation_email(user, confirmation_code)
        return Response(
            {
                "email": user.email,
                "username": user.username,
                # "role": user.role,
                # "first_name": user.first_name,
                # "last_name": user.last_name,
                # "bio": user.bio
            },
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


class ObtainAuthToken(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response(
                {"token": str(refresh.access_token)}, status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
