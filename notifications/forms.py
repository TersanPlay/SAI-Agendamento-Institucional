from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """Formulário para preferências de notificação"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'event_created', 'event_updated', 'event_cancelled',
            'event_reminder', 'event_starting', 'document_added',
            'participant_added', 'system_alert', 'reminder_hours'
        ]
        labels = {
            'event_created': 'Evento Criado',
            'event_updated': 'Evento Atualizado',
            'event_cancelled': 'Evento Cancelado',
            'event_reminder': 'Lembrete de Evento',
            'event_starting': 'Evento Iniciando',
            'document_added': 'Documento Adicionado',
            'participant_added': 'Participante Adicionado',
            'system_alert': 'Alertas do Sistema',
            'reminder_hours': 'Lembrete (horas antes)',
        }
        help_texts = {
            'reminder_hours': 'Quantas horas antes do evento você quer receber o lembrete',
        }
        widgets = {
            'event_created': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'event_updated': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'event_cancelled': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'event_reminder': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'event_starting': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'document_added': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'participant_added': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'system_alert': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
            }),
            'reminder_hours': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500',
                'min': '1',
                'max': '168'  # Max 1 week
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Group notifications by category
        self.notification_groups = {
            'Eventos': ['event_created', 'event_updated', 'event_cancelled'],
            'Lembretes': ['event_reminder', 'event_starting'],
            'Documentos e Participantes': ['document_added', 'participant_added'],
            'Sistema': ['system_alert'],
            'Configurações': ['reminder_hours'],
        }