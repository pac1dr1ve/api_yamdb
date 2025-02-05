from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    regex_validator = RegexValidator(
        regex=r"^[\w.@+_-]+\Z",
        message=_(
            "Можно использовать только буквы "
            "(включая буквы в верхнем и нижнем регистрах), "
            "цифры и спецсимволы: ., @, +, - "
        ),
        code="invalid_username",
    )
    regex_validator(value)


def validate_username_not_me(value):
    if value.lower() == "me":
        raise ValidationError(
            _("Использовать 'me' в качестве username запрещено."),
            code="invalid_username",
        )
