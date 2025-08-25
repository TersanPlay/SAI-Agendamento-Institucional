from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recipient', 'notification_type', 'priority',
        'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read', 'created_at'
    ]
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Destinatário e Tipo', {
            'fields': ('recipient', 'sender', 'notification_type', 'priority')
        }),
        ('Conteúdo', {
            'fields': ('title', 'message', 'event')
        }),
        ('Ação', {
            'fields': ('action_url', 'action_text')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'expires_at')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(is_read=True)
        self.message_user(request, f'{updated} notificações marcadas como lidas.')
    mark_as_read.short_description = 'Marcar como lida'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notificações marcadas como não lidas.')
    mark_as_unread.short_description = 'Marcar como não lida'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'event_created', 'event_updated', 'event_cancelled',
        'event_reminder', 'reminder_hours'
    ]
    list_filter = [
        'event_created', 'event_updated', 'event_cancelled',
        'event_reminder', 'system_alert'
    ]
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']