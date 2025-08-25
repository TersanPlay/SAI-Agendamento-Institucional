from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
import json
from .models import (
    Department, EventType, Location, Event, 
    EventHistory
    # EventDocument removed as requested
    # EventParticipant removed as requested
)


class MultipleVirtualLinksWidget(forms.Widget):
    """Custom widget to handle multiple virtual links"""
    template_name = 'admin/multiple_links_widget.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'vTextField'
    
    def format_value(self, value):
        if not value:
            return ''
        if isinstance(value, str):
            # If it's a single URL (for backward compatibility)
            return value
        if isinstance(value, list):
            # If it's a list of URLs, join them with newlines
            return '\n'.join(value)
        return str(value)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs.update(self.attrs)
        
        # Format the value for display
        formatted_value = self.format_value(value)
        
        # Create HTML for multiple input fields
        html_parts = []
        html_parts.append('<div class="multiple-links-container">')
        html_parts.append('<div class="help-text">Insira até 5 links virtuais (um por linha)</div>')
        
        # Create textarea for easier input
        textarea_attrs = attrs.copy()
        textarea_attrs.update({
            'rows': '5',
            'placeholder': 'https://exemplo1.com\nhttps://exemplo2.com\n...',
            'style': 'width: 100%; font-family: monospace;'
        })
        
        textarea_html = forms.Textarea().render(name, formatted_value, textarea_attrs)
        html_parts.append(textarea_html)
        
        html_parts.append('<div class="help-text">Máximo de 5 links. Insira um link por linha.</div>')
        html_parts.append('</div>')
        
        # Add inline styling instead of CSS block to avoid formatting issues
        help_style = 'style="font-size: 11px; color: #666; margin: 5px 0;"'
        html_parts[1] = f'<div class="help-text" {help_style}>Insira até 5 links virtuais (um por linha)</div>'
        html_parts[3] = f'<div class="help-text" {help_style}>Máximo de 5 links. Insira um link por linha.</div>'
        
        return format_html(''.join(html_parts))


class MultipleVirtualLinksField(forms.CharField):
    """Custom field to handle multiple virtual links"""
    widget = MultipleVirtualLinksWidget
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('help_text', 'Insira até 5 links virtuais, um por linha')
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value:
            return []
        
        if isinstance(value, list):
            return value
        
        # Split by newlines and filter out empty lines
        lines = [line.strip() for line in str(value).split('\n')]
        return [line for line in lines if line]
    
    def validate(self, value):
        super().validate(value)
        
        if not value:
            return
        
        # Check maximum number of links
        if len(value) > 5:
            raise ValidationError('Máximo de 5 links virtuais permitidos.')
        
        # Validate each URL
        from django.core.validators import URLValidator
        url_validator = URLValidator()
        
        for i, url in enumerate(value, 1):
            try:
                url_validator(url)
            except ValidationError:
                raise ValidationError(f'Link {i} não é uma URL válida: {url}')


class EventAdminForm(forms.ModelForm):
    """Custom admin form for Event model"""
    responsible_person_text = forms.CharField(
        max_length=200,
        label="Responsável do Evento",
        help_text="Digite o nome do responsável pelo evento",
        widget=forms.TextInput(attrs={
            'class': 'vTextField',
            'placeholder': 'Nome do responsável'
        })
    )
    
    virtual_links_multiple = MultipleVirtualLinksField(
        label="Links Virtuais",
        help_text="Insira até 5 links virtuais para eventos virtuais ou híbridos (um por linha)",
        required=False
    )
    
    class Meta:
        model = Event
        exclude = ['is_public']  # Only exclude is_public, keep responsible_person in model
        widgets = {
            'responsible_person': forms.HiddenInput(),  # Hide the original field
            'virtual_link': forms.HiddenInput(),  # Hide the original single virtual_link field
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle responsible person initialization
        if self.instance and self.instance.pk and hasattr(self.instance, 'responsible_person'):
            responsible = self.instance.responsible_person
            self.fields['responsible_person_text'].initial = responsible.get_full_name() or responsible.username
        else:
            # For new events, initialize with current user or first admin
            from django.contrib.auth.models import User
            try:
                current_user = getattr(self, '_current_user', None)
                if current_user:
                    self.fields['responsible_person_text'].initial = current_user.get_full_name() or current_user.username
                    self.fields['virtual_link'].initial = current_user
                else:
                    # Fallback to first superuser
                    admin_user = User.objects.filter(is_superuser=True).first()
                    if admin_user:
                        self.fields['responsible_person_text'].initial = admin_user.get_full_name() or admin_user.username
                        self.fields['responsible_person'].initial = admin_user
            except:
                pass
        
        # Handle virtual links initialization
        if self.instance and self.instance.pk:
            # Load existing virtual links
            try:
                # Check if virtual_link contains multiple URLs (JSON format) or single URL
                virtual_link_value = self.instance.virtual_link
                if virtual_link_value:
                    try:
                        # Try to parse as JSON (multiple links)
                        links_data = json.loads(virtual_link_value)
                        if isinstance(links_data, list):
                            self.fields['virtual_links_multiple'].initial = links_data
                        else:
                            # Single link stored as string
                            self.fields['virtual_links_multiple'].initial = [virtual_link_value]
                    except (json.JSONDecodeError, TypeError):
                        # Single URL string (backward compatibility)
                        self.fields['virtual_links_multiple'].initial = [virtual_link_value] if virtual_link_value else []
            except:
                self.fields['virtual_links_multiple'].initial = []
    
    def clean(self):
        cleaned_data = super().clean()
        responsible_text = cleaned_data.get('responsible_person_text', '')
        virtual_links = cleaned_data.get('virtual_links_multiple', [])
        
        # Handle responsible person
        if not cleaned_data.get('responsible_person'):
            from django.contrib.auth.models import User
            # Set to current user or first admin as fallback to satisfy the required constraint
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                cleaned_data['responsible_person'] = admin_user
        
        # Validate virtual links based on location mode
        location_mode = cleaned_data.get('location_mode')
        if location_mode in ['virtual', 'hibrido'] and not virtual_links:
            raise ValidationError({
                'virtual_links_multiple': 'Link virtual é obrigatório para eventos virtuais ou híbridos.'
            })
        
        # Convert virtual links list to JSON string for storage in the single virtual_link field
        if virtual_links:
            if len(virtual_links) == 1:
                # Store single link as string for backward compatibility
                cleaned_data['virtual_link'] = virtual_links[0]
            else:
                # Store multiple links as JSON
                cleaned_data['virtual_link'] = json.dumps(virtual_links)
        else:
            cleaned_data['virtual_link'] = ''
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set is_public to False by default since it's been removed from the interface
        instance.is_public = False
        
        if commit:
            instance.save()
        return instance


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


# EventDocumentInline removed as requested
# All document functionality has been eliminated


# EventParticipantInline removed as requested
# All participant functionality has been eliminated


class EventHistoryInline(admin.TabularInline):
    model = EventHistory
    extra = 0
    readonly_fields = ['field_name', 'old_value', 'new_value', 'changed_at', 'changed_by']
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = [
        'name', 'event_type', 'start_datetime', 'status', 
        'responsible_person', 'department'  # Removed 'is_public'
    ]
    list_filter = [
        'status', 'event_type', 'department', 'location_mode', 
        'target_audience', 'created_at'  # Removed 'is_public'
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
            'fields': ('location_mode', 'location', 'virtual_links_multiple')
        }),
        ('Responsabilidade', {
            'fields': ('responsible_person_text', 'department', 'target_audience')
        }),
        ('Status', {  # Renamed from 'Status e Visibilidade' and removed is_public
            'fields': ('status',)
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
    
    inlines = [EventHistoryInline]  # EventDocumentInline and EventParticipantInline removed
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Pass the current user to the form
        form._current_user = request.user
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
            # Set responsible_person to current user if not already set
            if not obj.responsible_person:
                obj.responsible_person = request.user
        super().save_model(request, obj, form, change)


# EventDocumentAdmin removed as requested
# All document functionality has been eliminated from the admin interface


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


# EventParticipantAdmin removed as requested
# All participant functionality has been eliminated from the admin interface
