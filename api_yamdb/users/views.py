import random
import string
from django.core.mail import send_mail
from rest_framework import status, views, viewsets, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsOwnerOrReadOnly
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
            except ValidationError as e:
                return Response({"error": e.detail},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        confirmation_code = self.generate_confirmation_code()

        user, created = User.objects.get_or_create(
            username=username,
            email=email
        )
        if created:
            # Новый пользователь
            user.confirmation_code = confirmation_code
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Пользователь уже существует, обновляем confirmation_code
            user.confirmation_code = confirmation_code
            user.save()
            return Response(
                {'detail': 'Код подтверждения отправлен повторно'},
                status=status.HTTP_200_OK
            )

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Неправильный пароль."]},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Пароль обновлен успешно',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def generate_confirmation_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits,
                                      k=50))

    @staticmethod
    def send_confirmation_email(user, confirmation_code=None):
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'yamdb@example.com',
            [user.email],
            fail_silently=False,
        )

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
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
        validated_data = serializer.is_valid(raise_exception=True)
        user = validated_data['user']
        if not user:
            raise exceptions.NotFound('Пользователь не найден')
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
