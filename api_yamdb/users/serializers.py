import random
import string

from django.core.mail import send_mail
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        confirmation_code = self.generate_confirmation_code()
        user = User.objects.create(**validated_data, confirmation_code=confirmation_code)
        self.send_confirmation_email(user, confirmation_code)
        return user

    @staticmethod
    def generate_confirmation_code():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=50))

    @staticmethod
    def send_confirmation_email(user, confirmation_code=None):
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'yamdb@example.com',
            [f"{user.email}"],
            fail_silently=False,
        )
