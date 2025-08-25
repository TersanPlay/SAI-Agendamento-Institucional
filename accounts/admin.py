from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, AccessLog


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = UserAdmin.list_display + ('get_user_type', 'get_department')
    list_filter = UserAdmin.list_filter + ('profile__user_type', 'profile__department')
    
    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return '-'
    get_user_type.short_description = 'Tipo de Usuário'
    
    def get_department(self, obj):
        if hasattr(obj, 'profile') and obj.profile.department:
            return obj.profile.department.name
        return '-'
    get_department.short_description = 'Departamento'


# Substituir o admin padrão do User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'user_type', 'department', 'phone', 
        'receive_notifications', 'created_at'
    ]
    list_filter = ['user_type', 'department', 'receive_notifications', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'resource', 'ip_address', 
        'timestamp', 'success'
    ]
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['user__username', 'action', 'resource', 'ip_address']
    readonly_fields = [
        'user', 'action', 'resource', 'ip_address', 
        'user_agent', 'timestamp', 'success'
    ]
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False