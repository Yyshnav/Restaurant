# Restaurant/Accountapp/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LoginTable, UserRole

class LoginTableAdmin(UserAdmin):
    model = LoginTable

    # Add your custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'otp', 'user_roles', 'created_at')
        }),
    )

    # For better ManyToMany widget in admin
    filter_horizontal = ('user_roles',)

    # Display in list view
    list_display = ('username', 'phone', 'is_active', 'get_roles', 'last_login')
    list_filter = ('is_active', 'user_roles')

    # Read-only fields
    readonly_fields = ('created_at',)

    def get_roles(self, obj):
        return ", ".join([role.role for role in obj.user_roles.all()])
    get_roles.short_description = 'Roles'

admin.site.register(LoginTable, LoginTableAdmin)
# admin.site.register(UserRole)
