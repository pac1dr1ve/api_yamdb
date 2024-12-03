from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class UserRegistrationView(views.APIView):
    permission_classes = (AllowAny,)
    model = get_user_model()

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = ('email', 'username', 'password')

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = self.model.objects.make_random_password()
            email = serializer.validated_data['email']
            send_mail(
                'Confirmation code',
                confirmation_code,
                'from@example.com',
                [email],
                fail_silently=False,
            )
            self.model.objects.create_user(
                username=serializer.validated_data['username'],
                email=email,
                password=serializer.validated_data['password'],
                confirmation_code=confirmation_code
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshToken:
    @classmethod
    def for_user(cls, user):
        pass


class ConfirmationCodeView(views.APIView):
    permission_classes = (AllowAny,)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = ('username', 'confirmation_code')

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            get_user_model(),
            username=serializer.validated_data['username']
        )
        if user.confirmation_code == serializer.validated_data['confirmation_code']:
            token = RefreshToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
