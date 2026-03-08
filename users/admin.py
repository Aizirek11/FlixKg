from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('phone', 'avatar', 'date_of_birth')}),
    )
# Register your models here.
