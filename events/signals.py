from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Event, EventHistory
from notifications.services import NotificationService


@receiver(pre_save, sender=Event)
def track_event_changes(sender, instance, **kwargs):
    """Registra mudanças nos eventos para o histórico"""
    if instance.pk:  # Se o evento já existe
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            changes = []
            
            # Campos a serem monitorados
            tracked_fields = {
                'name': 'Nome do Evento',
                'event_type': 'Tipo de Evento',
                'start_datetime': 'Data/Hora de Início',
                'end_datetime': 'Data/Hora de Término',
                'location_mode': 'Modalidade',
                'location': 'Localização',
                'virtual_link': 'Link Virtual',
                'target_audience': 'Público-alvo',
                'responsible_person': 'Responsável',
                'department': 'Departamento',
                'status': 'Status',
                'description': 'Descrição',
                'is_public': 'Evento Público',
            }
            
            for field, field_name in tracked_fields.items():
                old_value = getattr(old_instance, field, None)
                new_value = getattr(instance, field, None)
                
                # Converter valores para string para comparação
                if old_value != new_value:
                    old_str = str(old_value) if old_value is not None else ''
                    new_str = str(new_value) if new_value is not None else ''
                    
                    changes.append({
                        'field_name': field_name,
                        'old_value': old_str,
                        'new_value': new_str,
                    })
            
            # Armazenar mudanças para criar o histórico após o save
            instance._changes = changes
            
        except Event.DoesNotExist:
            instance._changes = []
    else:
        instance._changes = []


@receiver(post_save, sender=Event)
def create_event_history(sender, instance, created, **kwargs):
    """Cria registros de histórico após salvar o evento"""
    from django.contrib.auth.models import AnonymousUser
    
    # Obter o usuário atual (pode ser passado no contexto)
    user = getattr(instance, '_current_user', None)
    if not user or isinstance(user, AnonymousUser):
        # Fallback para o usuário que criou o evento
        user = instance.created_by
    
    if created:
        # Evento criado
        EventHistory.objects.create(
            event=instance,
            field_name='Evento Criado',
            old_value='',
            new_value=f'Evento "{instance.name}" criado',
            changed_by=user
        )
        
        # Criar notificação de evento criado
        NotificationService.create_event_notification(
            event=instance,
            notification_type='event_created',
            sender=user
        )
    else:
        # Evento atualizado - criar registros para cada mudança
        changes = getattr(instance, '_changes', [])
        for change in changes:
            EventHistory.objects.create(
                event=instance,
                field_name=change['field_name'],
                old_value=change['old_value'],
                new_value=change['new_value'],
                changed_by=user
            )
        
        # Se houve mudanças, criar notificação
        if changes:
            NotificationService.create_event_notification(
                event=instance,
                notification_type='event_updated',
                sender=user
            )


@receiver(post_save, sender=Event)
def handle_status_changes(sender, instance, created, **kwargs):
    """Lida com mudanças de status do evento"""
    if not created and hasattr(instance, '_changes'):
        status_changed = any(
            change['field_name'] == 'Status' 
            for change in instance._changes
        )
        
        if status_changed:
            if instance.status == 'cancelado':
                # Notificar sobre cancelamento
                NotificationService.create_event_notification(
                    event=instance,
                    notification_type='event_cancelled'
                )
            elif instance.status == 'concluido':
                # Notificar sobre conclusão
                NotificationService.create_event_notification(
                    event=instance,
                    notification_type='event_ended'
                )