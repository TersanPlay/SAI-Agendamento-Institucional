from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Notification, NotificationPreference
from events.models import Event


class NotificationService:
    """Service for managing automatic notifications"""
    
    @staticmethod
    def create_event_notification(event, notification_type, recipients=None, sender=None):
        """Cria notificações relacionadas a eventos"""
        if recipients is None:
            # Determine recipients based on event and notification type
            recipients = NotificationService._get_event_recipients(event, notification_type)
        
        notifications_created = []
        
        for recipient in recipients:
            # Check user preferences
            preferences = NotificationService._get_user_preferences(recipient)
            if not NotificationService._should_send_notification(notification_type, preferences):
                continue
            
            # Determine priority based on notification type
            priority = NotificationService._get_priority_for_type(notification_type)
            
            # Create notification
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender or event.created_by,
                notification_type=notification_type,
                priority=priority,
                title=NotificationService._get_notification_title(event, notification_type),
                message=NotificationService._get_notification_message(event, notification_type),
                event=event,
                action_url=event.get_absolute_url() if event else None,
                action_text="Ver Evento" if event else None
            )
            
            notifications_created.append(notification)
        
        return notifications_created
    
    @staticmethod
    def create_reminder_notifications():
        """Cria notificações de lembrete para eventos próximos"""
        now = timezone.now()
        notifications_created = []
        
        # Get all users with reminder preferences
        users_with_reminders = User.objects.filter(
            notification_preferences__event_reminder=True
        ).select_related('notification_preferences')
        
        for user in users_with_reminders:
            preferences = user.notification_preferences
            reminder_time = now + timedelta(hours=preferences.reminder_hours)
            
            # Find events that need reminders
            events_needing_reminders = Event.objects.filter(
                start_datetime__gte=now + timedelta(hours=preferences.reminder_hours - 1),
                start_datetime__lte=now + timedelta(hours=preferences.reminder_hours + 1),
                status__in=['planejado', 'em_andamento']
            ).exclude(
                # Exclude events that already have reminder notifications for this user
                notifications__recipient=user,
                notifications__notification_type='event_reminder',
                notifications__created_at__gte=now - timedelta(hours=1)
            )
            
            # Filter events user can access
            from accounts.utils import get_user_accessible_events
            accessible_events = get_user_accessible_events(user)
            events_needing_reminders = events_needing_reminders.filter(
                id__in=accessible_events.values_list('id', flat=True)
            )
            
            for event in events_needing_reminders:
                notification = Notification.objects.create(
                    recipient=user,
                    sender=None,
                    notification_type='event_reminder',
                    priority='medium',
                    title=f"Lembrete: {event.name}",
                    message=f"O evento '{event.name}' começará em {preferences.reminder_hours} hora(s).",
                    event=event,
                    action_url=event.get_absolute_url(),
                    action_text="Ver Detalhes"
                )
                notifications_created.append(notification)
        
        return notifications_created
    
    @staticmethod
    def create_system_notification(title, message, recipients=None, priority='medium', sender=None):
        """Cria notificação do sistema"""
        if recipients is None:
            # Send to all active users if no recipients specified
            recipients = User.objects.filter(is_active=True)
        
        notifications_created = []
        
        for recipient in recipients:
            preferences = NotificationService._get_user_preferences(recipient)
            if not preferences.system_alert:
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type='system_alert',
                priority=priority,
                title=title,
                message=message
            )
            notifications_created.append(notification)
        
        return notifications_created
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Remove notificações antigas"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        return deleted_count
    
    @staticmethod
    def _get_event_recipients(event, notification_type):
        """Determina os destinatários para notificações de evento"""
        recipients = set()
        
        # Always include event responsible person
        recipients.add(event.responsible_person)
        
        # Include department members for certain types
        if notification_type in ['event_created', 'event_updated', 'event_cancelled']:
            if event.department:
                dept_users = User.objects.filter(
                    profile__department=event.department,
                    profile__user_type__in=['administrador', 'gestor']
                )
                recipients.update(dept_users)
        
        # Include administrators for important notifications
        if notification_type in ['event_cancelled']:
            admins = User.objects.filter(profile__user_type='administrador')
            recipients.update(admins)
        
        # Participant-related notifications removed as requested
        
        # Remove the person who triggered the action
        if event.created_by in recipients:
            recipients.remove(event.created_by)
        
        return list(recipients)
    
    @staticmethod
    def _get_user_preferences(user):
        """Obtém preferências de notificação do usuário"""
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        return preferences
    
    @staticmethod
    def _should_send_notification(notification_type, preferences):
        """Verifica se deve enviar notificação baseado nas preferências"""
        type_mapping = {
            'event_created': preferences.event_created,
            'event_updated': preferences.event_updated,
            'event_cancelled': preferences.event_cancelled,
            'event_reminder': preferences.event_reminder,
            'event_starting': preferences.event_starting,
            # 'document_added': preferences.document_added, - Removed as requested
            # 'participant_added': preferences.participant_added, - Removed as requested
            'system_alert': preferences.system_alert,
        }
        
        return type_mapping.get(notification_type, True)
    
    @staticmethod
    def _get_priority_for_type(notification_type):
        """Determina prioridade baseada no tipo de notificação"""
        priority_mapping = {
            'event_cancelled': 'high',
            'event_reminder': 'medium',
            'event_starting': 'high',
            'system_alert': 'high',
            'event_created': 'low',
            'event_updated': 'low',
            # 'document_added': 'low', - Removed as requested
            # 'participant_added': 'low', - Removed as requested
        }
        
        return priority_mapping.get(notification_type, 'medium')
    
    @staticmethod
    def _get_notification_title(event, notification_type):
        """Gera título da notificação"""
        titles = {
            'event_created': f"Novo evento: {event.name}",
            'event_updated': f"Evento atualizado: {event.name}",
            'event_cancelled': f"Evento cancelado: {event.name}",
            'event_reminder': f"Lembrete: {event.name}",
            'event_starting': f"Evento iniciando: {event.name}",
            # 'document_added': f"Documento adicionado: {event.name}", - Removed as requested
            # 'participant_added': f"Participante adicionado: {event.name}", - Removed as requested
        }
        
        return titles.get(notification_type, f"Notificação: {event.name}")
    
    @staticmethod
    def _get_notification_message(event, notification_type):
        """Gera mensagem da notificação"""
        messages = {
            'event_created': f"Um novo evento '{event.name}' foi criado para {event.start_datetime.strftime('%d/%m/%Y às %H:%M')}.",
            'event_updated': f"O evento '{event.name}' foi atualizado. Verifique as alterações.",
            'event_cancelled': f"O evento '{event.name}' que estava agendado para {event.start_datetime.strftime('%d/%m/%Y às %H:%M')} foi cancelado.",
            'event_reminder': f"O evento '{event.name}' começará em breve ({event.start_datetime.strftime('%d/%m/%Y às %H:%M')}).",
            'event_starting': f"O evento '{event.name}' está começando agora!",
            # 'document_added': f"Um novo documento foi adicionado ao evento '{event.name}'.", - Removed as requested
            # 'participant_added': f"Um novo participante foi adicionado ao evento '{event.name}'.", - Removed as requested
        }
        
        return messages.get(notification_type, f"Notificação sobre o evento '{event.name}'.")
