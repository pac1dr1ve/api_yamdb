from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class UsernameValidationMixin:
    username_validator = RegexValidator(
        regex=r"^[\w.@+_-]+\Z",
        message=_(
            "Можно использовать только буквы "
            "(включая буквы в верхнем и нижнем регистрах), "
            "цифры и спецсимволы: ., @, +, - "
        ),
        code="invalid_username",
    )

    def validate_username(self, username):
        self.username_validator(username)
        if username.lower() == "me":
            raise ValidationError(
                _("Использовать 'me' в качестве username запрещено."),
                code="invalid_username",
            )
        return username
