from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Event, EventType, Location, Department  # EventDocument removed
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML


class EventForm(forms.ModelForm):
    """Formulário principal para criação e edição de eventos"""
    
    # Custom responsible person text field to match admin interface
    responsible_person_text = forms.CharField(
        max_length=200,
        label='Responsável do Evento',
        help_text='Digite o nome do responsável pelo evento',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nome do responsável'
        })
    )
    
    # Override virtual_link field to handle multiple URLs
    virtual_link = forms.CharField(
        label='Links Virtuais',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Insira até 5 links virtuais (um por linha):\nhttps://exemplo1.com\nhttps://exemplo2.com'
        }),
        help_text='Insira até 5 links virtuais, um por linha. Para eventos virtuais ou híbridos.'
    )
    
    class Meta:
        model = Event
        fields = [
            'name', 'event_type', 'start_datetime', 'end_datetime',
            'location_mode', 'location', 'virtual_link', 'target_audience',
            'responsible_person', 'department', 'status', 'description',
            'observations'
        ]
        labels = {
            'name': 'Nome do Evento',
            'event_type': 'Tipo de Evento',
            'start_datetime': 'Data/Hora de Início',
            'end_datetime': 'Data/Hora de Término',
            'location_mode': 'Modalidade',
            'location': 'Localização',
            'target_audience': 'Público-alvo',
            'responsible_person': 'Responsável do Evento',
            'department': 'Departamento Responsável',
            'status': 'Status',
            'description': 'Descrição',
            'observations': 'Observações',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Digite o nome do evento'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Descrição detalhada do evento'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observações adicionais'
            }),
            'event_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'location_mode': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'location': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'responsible_person': forms.HiddenInput(),  # Hide the original field
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Handle responsible person initialization
        if self.instance and self.instance.pk and hasattr(self.instance, 'responsible_person'):
            responsible = self.instance.responsible_person
            self.fields['responsible_person_text'].initial = responsible.get_full_name() or responsible.username
        else:
            # For new events, initialize with current user
            if self.user:
                self.fields['responsible_person_text'].initial = self.user.get_full_name() or self.user.username
                self.fields['responsible_person'].initial = self.user
            else:
                # Fallback to first admin user
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    self.fields['responsible_person_text'].initial = admin_user.get_full_name() or admin_user.username
                    self.fields['responsible_person'].initial = admin_user
        
        # Se é um usuário gestor, filtrar departamento
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.is_manager and self.user.profile.department:
                self.fields['department'].initial = self.user.profile.department
        
        # Handle virtual links initialization for editing
        if self.instance and self.instance.pk and self.instance.virtual_link:
            try:
                import json
                # Try to parse as JSON (multiple links)
                links_data = json.loads(self.instance.virtual_link)
                if isinstance(links_data, list):
                    # Display multiple links, one per line
                    self.fields['virtual_link'].initial = '\n'.join(links_data)
                else:
                    # Single link (fallback)
                    self.fields['virtual_link'].initial = self.instance.virtual_link
            except (json.JSONDecodeError, TypeError):
                # Single URL string (backward compatibility)
                self.fields['virtual_link'].initial = self.instance.virtual_link

    def clean_virtual_link(self):
        """Clean and validate virtual links"""
        virtual_link = self.cleaned_data.get('virtual_link', '')
        
        if not virtual_link:
            return ''
        
        # Split by newlines and filter out empty lines
        lines = [line.strip() for line in virtual_link.split('\n') if line.strip()]
        
        if not lines:
            return ''
        
        # Validate maximum number of links
        if len(lines) > 5:
            raise ValidationError("Máximo de 5 links virtuais permitidos.")
        
        # Validate each URL
        from django.core.validators import URLValidator
        url_validator = URLValidator()
        
        valid_links = []
        for i, url in enumerate(lines, 1):
            try:
                url_validator(url)
                valid_links.append(url)
            except ValidationError:
                raise ValidationError(f"Link {i} não é uma URL válida: {url}")
        
        # Convert to storage format
        if len(valid_links) == 1:
            return valid_links[0]  # Single link as string
        elif len(valid_links) > 1:
            import json
            return json.dumps(valid_links)  # Multiple links as JSON
        
        return ''
    
    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        location_mode = cleaned_data.get('location_mode')
        virtual_link = cleaned_data.get('virtual_link')
        location = cleaned_data.get('location')
        responsible_text = cleaned_data.get('responsible_person_text', '')
        
        # Handle responsible person - set to current user as fallback
        if not cleaned_data.get('responsible_person'):
            if self.user:
                cleaned_data['responsible_person'] = self.user
            else:
                # Fallback to first admin user
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    cleaned_data['responsible_person'] = admin_user
        
        # Validar datas
        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise ValidationError("A data de início deve ser anterior à data de término.")
        
        # Validar link virtual baseado na modalidade
        if location_mode in ['virtual', 'hibrido'] and not virtual_link:
            raise ValidationError("Link virtual é obrigatório para eventos virtuais ou híbridos.")
        
        # Validar localização física
        if location_mode in ['presencial', 'hibrido'] and not location:
            raise ValidationError("Localização é obrigatória para eventos presenciais ou híbridos.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set is_public to False by default since it's been removed from the interface
        instance.is_public = False
        
        if commit:
            instance.save()
        return instance


# EventDocumentForm has been removed as requested


# EventParticipantForm has been removed as requested
# All participant functionality has been eliminated


class EventFilterForm(forms.Form):
    """Formulário para filtros de eventos"""
    
    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.all(), # type: ignore
        required=False,
        empty_label="Todos os tipos",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), # type: ignore
        required=False,
        empty_label="Todos os departamentos",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Event.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    responsible_person = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__user_type__in=['gestor', 'administrador']),
        required=False,
        empty_label="Todos os responsáveis",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Buscar por nome, descrição...'
        })
    )


# Formsets have been removed (documents and participants functionality eliminated)
# EventDocumentFormSet has been removed as requested
# EventParticipantFormSet has been removed as requested