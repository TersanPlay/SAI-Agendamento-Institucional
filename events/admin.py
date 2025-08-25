from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department, EventType, Location, Event, 
    EventDocument, EventHistory, EventParticipant
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'color_preview', 'icon']
    list_filter = ['name']
    search_fields = ['name']
    
    def display_name(self, obj):
        return obj.get_name_display()
    display_name.short_description = 'Tipo'  # type: ignore
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Cor'  # type: ignore


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'custom_name', 'capacity']
    list_filter = ['name']
    search_fields = ['name', 'custom_name']
    
    def display_name(self, obj):
        return obj.get_name_display()
    display_name.short_description = 'Localização'  # type: ignore


class EventDocumentInline(admin.TabularInline):
    model = EventDocument
    extra = 0
    max_num = 5


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    readonly_fields = ['added_at']


class EventHistoryInline(admin.TabularInline):
    model = EventHistory
    extra = 0
    readonly_fields = ['field_name', 'old_value', 'new_value', 'changed_at', 'changed_by']
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'event_type', 'start_datetime', 'status', 
        'responsible_person', 'department', 'is_public'
    ]
    list_filter = [
        'status', 'event_type', 'department', 'location_mode', 
        'target_audience', 'is_public', 'created_at'
    ]
    search_fields = ['name', 'description', 'responsible_person__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'event_type', 'description')
        }),
        ('Data e Horário', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Local e Modalidade', {
            'fields': ('location_mode', 'location', 'virtual_link')
        }),
        ('Responsabilidade', {
            'fields': ('responsible_person', 'department', 'target_audience')
        }),
        ('Status e Visibilidade', {
            'fields': ('status', 'is_public')
        }),
        ('Observações', {
            'fields': ('observations',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EventDocumentInline, EventParticipantInline, EventHistoryInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'external_link', 'created_at', 'created_by']
    list_filter = ['created_at']
    search_fields = ['title', 'event__name']
    readonly_fields = ['created_at', 'created_by']


@admin.register(EventHistory)
class EventHistoryAdmin(admin.ModelAdmin):
    list_display = ['event', 'field_name', 'changed_at', 'changed_by']
    list_filter = ['field_name', 'changed_at']
    search_fields = ['event__name', 'field_name']
    readonly_fields = ['event', 'field_name', 'old_value', 'new_value', 'changed_at', 'changed_by']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['event', 'get_participant_name', 'confirmed', 'attended', 'added_at']
    list_filter = ['confirmed', 'attended', 'added_at']
    search_fields = ['event__name', 'user__username', 'name', 'email']
    readonly_fields = ['added_at']
    
    def get_participant_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return obj.name
    get_participant_name.short_description = 'Participante'  # type: ignore
