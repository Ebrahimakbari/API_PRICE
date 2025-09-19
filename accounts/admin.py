from django.contrib import admin
from .models import CustomUser




@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    ordering = ('email', 'phone_number', 'first_name', 'last_name')
