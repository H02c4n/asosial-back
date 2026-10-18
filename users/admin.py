from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Varsayılan UserAdmin'e ek alanlar (bio, avatar, following)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profil', {'fields': ('bio', 'avatar', 'following')}),
    )
    list_display = ('username', 'email', 'is_active', 'date_joined')
    filter_horizontal = BaseUserAdmin.filter_horizontal + ('following',)