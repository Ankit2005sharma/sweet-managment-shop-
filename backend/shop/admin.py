from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Sweet, Order


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name')
    ordering = ('email',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )


@admin.register(Sweet)
class SweetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'sweet', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'sweet__name')
    readonly_fields = ('created_at',)