import random
import re
import string

from django.core.mail import send_mail
from rest_framework import status, viewsets, permissions, generics, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, Enum
from users.permissions import CustomIsAdminUserOrSuperuser
from users.serializers import SignUpSerializer, UserSerializer, UserTokenSerializer, ChangePasswordSerializer


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
    queryset = User.objects.all()
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
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['destroy', 'retrieve', 'partial_update', 'update']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser(), ]

    def check_password(self, user, old_password):
        """Проверка пароля на корректность"""
        if not user.check_password(old_password):
            return False
        return True

    def update_password(self, user, new_password):
        """Обновление пароля пользователя"""
        user.set_password(new_password)
        user.save()

    # def update(self, request, *args, **kwargs):
    #     user = get_object_or_404(User, username=self.kwargs["username"])
    #     serializer = ChangePasswordSerializer(data=request.data)
    #
    #     if serializer.is_valid():
    #         if not self.check_password(user, serializer.validated_data["old_password"]):
    #             return Response({"old_password": ["Неправильный пароль."]}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         if 'password' not in request.data:
    #             instance = self.get_object()
    #             serializer = self.get_serializer(instance, data=request.data, partial=True)
    #             serializer.is_valid(raise_exception=True)
    #             self.perform_update(serializer)
    #
    #             if getattr(instance, '_prefetched_objects_cache', None):
    #                 instance._prefetched_objects_cache = {}
    #
    #             return Response(serializer.data)
    #
    #         else:
    #
    #             self.update_password(user, serializer.validated_data["new_password"])
    #             return Response({
    #                 "status": "success",
    #                 "code": status.HTTP_200_OK,
    #                 "message": "Пароль обновлен успешно",
    #                 "data": [],
    #             }, status=status.HTTP_200_OK)
    #
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def update(self, request, *args, **kwargs):
    #     user = get_object_or_404(User, username=self.kwargs["username"])
    #     serializer = ChangePasswordSerializer(data=request.data)
    #     permissions = CustomIsAdminUserOrSuperuser
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
    #     return Response("Недоступно", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(detail=False, methods=['delete'])  # Метод удаления пользователя должен быть доступен только администратору
    # def user_delete(self, request):
    #     user = self.get_object()
    #     if not request.user.is_staff:
    #         return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
    #
    #     user.delete()
    #     return Response("Пользователь успешно удален", status=status.HTTP_204_NO_CONTENT)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

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
