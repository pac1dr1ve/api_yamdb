from users.validators import (validate_username_me,
                              validate_username_regex)


class UsernameValidationMixin:
    def validate_username(self, username):
        """
        Проверяем имя пользователя на регулярное выражение
        и дополнительному правилу (запрет на использование "me" в username).
        """
        validate_username_regex(username)
        validate_username_me(username)
        return username
