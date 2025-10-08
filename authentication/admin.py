from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserActionLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target_model', 'target_id', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'details', 'ip_address']
    readonly_fields = ['user', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'user_agent', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
