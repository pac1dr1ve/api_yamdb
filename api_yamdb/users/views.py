import random
import string

from django.core.mail import send_mail
from rest_framework import status, views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (UserSerializer,
                          UserRegistrationSerializer,
                          UserTokenSerializer)


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
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
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
            self.send_confirmation_email(user, confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Пользователь уже существует, обновляем confirmation_code
            user.confirmation_code = confirmation_code
            user.save()
            self.send_confirmation_email(user, confirmation_code)
            return Response(
                {'detail': 'Код подтверждения отправлен повторно'},
                status=status.HTTP_200_OK
            )

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


class ObtainAuthToken(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        validated_data = serializer.is_valid(raise_exception=True)
        user = validated_data['user']
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
