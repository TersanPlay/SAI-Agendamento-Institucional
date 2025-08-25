from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """Sistema de notificações internas"""
    
    NOTIFICATION_TYPES = [
        ('event_created', 'Evento Criado'),
        ('event_updated', 'Evento Atualizado'),
        ('event_cancelled', 'Evento Cancelado'),
        ('event_reminder', 'Lembrete de Evento'),
        ('event_starting', 'Evento Iniciando'),
        ('event_ended', 'Evento Finalizado'),
        # ('document_added', 'Documento Adicionado'), - Removed as requested
        # ('participant_added', 'Participante Adicionado'), - Removed as requested
        ('system_alert', 'Alerta do Sistema'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                                verbose_name="Destinatário")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='sent_notifications', verbose_name="Remetente")
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES,
                                       verbose_name="Tipo de Notificação")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium',
                              verbose_name="Prioridade")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    
    # Relacionamento com evento (opcional)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='notifications', verbose_name="Evento Relacionado")
    
    # Status da notificação
    is_read = models.BooleanField(default=False, verbose_name="Lida")  # type: ignore
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Lida em")
    
    # URLs e ações
    action_url = models.URLField(blank=True, verbose_name="URL da Ação")
    action_text = models.CharField(max_length=50, blank=True, verbose_name="Texto da Ação")
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira em")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Marca a notificação como lida"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Verifica se a notificação expirou"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @classmethod
    def create_event_notification(cls, event, notification_type, recipients=None):
        """Cria notificações relacionadas a eventos"""
        if recipients is None:
            # Notificar responsável e departamento por padrão
            recipients = [event.responsible_person]
            if event.department:
                dept_users = User.objects.filter(profile__department=event.department)
                recipients.extend(dept_users)
        
        notifications = []
        for recipient in recipients:
            if recipient != event.created_by:  # Não notificar quem criou
                notification = cls.objects.create(
                    recipient=recipient,
                    sender=event.created_by,
                    notification_type=notification_type,
                    title=f"Evento: {event.name}",
                    message=f"O evento '{event.name}' foi {cls._get_action_text(notification_type)}.",
                    event=event,
                    action_url=event.get_absolute_url(),
                    action_text="Ver Evento"
                )
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def _get_action_text(notification_type):
        """Retorna o texto da ação baseado no tipo de notificação"""
        action_map = {
            'event_created': 'criado',
            'event_updated': 'atualizado',
            'event_cancelled': 'cancelado',
            'event_reminder': 'tem início em breve',
            'event_starting': 'está iniciando',
            'event_ended': 'foi finalizado',
        }
        return action_map.get(notification_type, 'modificado')


class NotificationPreference(models.Model):
    """Preferências de notificação do usuário"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Tipos de notificação que o usuário quer receber
    event_created = models.BooleanField(default=True, verbose_name="Evento Criado")  # type: ignore
    event_updated = models.BooleanField(default=True, verbose_name="Evento Atualizado")  # type: ignore
    event_cancelled = models.BooleanField(default=True, verbose_name="Evento Cancelado")  # type: ignore
    event_reminder = models.BooleanField(default=True, verbose_name="Lembrete de Evento")  # type: ignore
    event_starting = models.BooleanField(default=True, verbose_name="Evento Iniciando")  # type: ignore
    # document_added field removed as requested
    # participant_added field removed as requested
    system_alert = models.BooleanField(default=True, verbose_name="Alertas do Sistema")  # type: ignore
    
    # Configurações de tempo
    reminder_hours = models.PositiveIntegerField(default=24, verbose_name="Lembrete (horas antes)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preferência de Notificação"
        verbose_name_plural = "Preferências de Notificação"
    
    def __str__(self):
        return f"Preferências de {self.user.username}"