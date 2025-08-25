from django.contrib import admin
from .models import Dashboard


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'is_default', 'default_period_days',
        'created_at'
    ]
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'user', 'is_default')
        }),
        ('Widgets', {
            'fields': (
                'show_events_today', 'show_events_week',
                'show_events_by_type', 'show_events_by_status',
                'show_recent_activity', 'show_my_events'
            )
        }),
        ('Configurações', {
            'fields': ('default_period_days',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )