from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, Role


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('username', 'email',
                           'first_name', 'last_name', 'bio', 'role')}),
    )
    readonly_fields = ('confirmation_code',)
    empty_value_display = 'Не задано'

    def save_model(self, request, obj, form, change):
        if obj.role == Role.ADMIN.value:
            obj.is_staff = True
            obj.is_superuser = True
        elif obj.role == Role.MODERATOR.value:
            obj.is_staff = True
            obj.is_superuser = False
        obj.save()
