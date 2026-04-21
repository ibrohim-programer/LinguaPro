from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
       "id" ,'username', 'full_name', 'role', 'phone', 'is_active', 'created_at'
    ]

    list_filter = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy', {
            'fields': ('username', 'password')
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'phone', 'avatar')
        }),
        ('Rol va holat', {
            'fields': ('role', 'is_active')
        }),
        ('Qo\'shimcha', {
            'fields': ('timezone', 'bio', 'learning_goal')
        }),
    )

    add_fieldsets = (
        ('Yangi foydalanuvchi', {
            'fields': ('username', 'password1', 'password2', 'role', 'first_name', 'last_name')
        }),
    )