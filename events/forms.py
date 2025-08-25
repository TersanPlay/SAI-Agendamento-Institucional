from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Event, EventType, Location, Department, EventDocument, EventParticipant
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML


class EventForm(forms.ModelForm):
    """Formulário principal para criação e edição de eventos"""
    
    class Meta:
        model = Event
        fields = [
            'name', 'event_type', 'start_datetime', 'end_datetime',
            'location_mode', 'location', 'virtual_link', 'target_audience',
            'responsible_person', 'department', 'status', 'description',
            'observations', 'is_public'
        ]
        labels = {
            'name': 'Nome do Evento',
            'event_type': 'Tipo de Evento',
            'start_datetime': 'Data/Hora de Início',
            'end_datetime': 'Data/Hora de Término',
            'location_mode': 'Modalidade',
            'location': 'Localização',
            'virtual_link': 'Link Virtual',
            'target_audience': 'Público-alvo',
            'responsible_person': 'Responsável do Evento',
            'department': 'Departamento Responsável',
            'status': 'Status',
            'description': 'Descrição',
            'observations': 'Observações',
            'is_public': 'Evento Público',
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
            'virtual_link': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://exemplo.com/reuniao'
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
            'responsible_person': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar usuários responsáveis (apenas gestores e administradores)
        responsible_users = User.objects.filter(
            profile__user_type__in=['gestor', 'administrador']
        ).select_related('profile')
        self.fields['responsible_person'].queryset = responsible_users
        
        # Se é um usuário gestor, filtrar departamento
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.is_manager and self.user.profile.department:
                self.fields['department'].initial = self.user.profile.department

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        location_mode = cleaned_data.get('location_mode')
        virtual_link = cleaned_data.get('virtual_link')
        location = cleaned_data.get('location')
        
        # Validar datas
        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise ValidationError("A data de início deve ser anterior à data de término.")
        
        # Validar link virtual
        if location_mode in ['virtual', 'hibrido'] and not virtual_link:
            raise ValidationError("Link virtual é obrigatório para eventos virtuais ou híbridos.")
        
        # Validar localização física
        if location_mode in ['presencial', 'hibrido'] and not location:
            raise ValidationError("Localização é obrigatória para eventos presenciais ou híbridos.")
        
        return cleaned_data


class EventDocumentForm(forms.ModelForm):
    """Formulário para documentos/termos de responsabilidade"""
    
    class Meta:
        model = EventDocument
        fields = ['title', 'external_link', 'uploaded_file']
        labels = {
            'title': 'Título do Documento',
            'external_link': 'Link Externo',
            'uploaded_file': 'Arquivo (opcional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: Termo de Responsabilidade'
            }),
            'external_link': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://documento.exemplo.com'
            }),
            'uploaded_file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })
        }


class EventParticipantForm(forms.ModelForm):
    """Formulário para adicionar participantes"""
    
    class Meta:
        model = EventParticipant
        fields = ['user', 'name', 'email']
        labels = {
            'user': 'Usuário do Sistema',
            'name': 'Nome (para externos)',
            'email': 'Email',
        }
        widgets = {
            'user': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do participante externo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@exemplo.com'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        name = cleaned_data.get('name')
        
        if not user and not name:
            raise ValidationError("Selecione um usuário do sistema ou informe o nome do participante externo.")
        
        return cleaned_data


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


# Formsets para documentos e participantes
from django.forms import inlineformset_factory

EventDocumentFormSet = inlineformset_factory(
    Event, EventDocument, form=EventDocumentForm,
    extra=1, max_num=5, can_delete=True
)

EventParticipantFormSet = inlineformset_factory(
    Event, EventParticipant, form=EventParticipantForm,
    extra=1, can_delete=True
)