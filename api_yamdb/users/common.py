import random
import string

from django.core.mail import send_mail
from django.conf import settings

from reviews.constants import MAX_CONFORMATION_CODE_STRING


class UserService:
    @staticmethod
    def create_confirmation_code():
        confirmation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits,
                           k=MAX_CONFORMATION_CODE_STRING),
        )
        return confirmation_code

    @staticmethod
    def send_confirmation_email(user, confirmation_code):
        send_mail(
            "Код подтверждения",
            f"Ваш код подтверждения: {confirmation_code}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
