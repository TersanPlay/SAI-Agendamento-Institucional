from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm
from accounts.utils import log_user_action


@login_required
def notification_list(request):
    """Lista de notificações do usuário"""
    notifications = request.user.notifications.order_by('-created_at')
    
    # Filtros
    filter_type = request.GET.get('type', '')
    filter_read = request.GET.get('read', '')
    
    if filter_type:
        notifications = notifications.filter(notification_type=filter_type)
    
    if filter_read == 'true':
        notifications = notifications.filter(is_read=True)
    elif filter_read == 'false':
        notifications = notifications.filter(is_read=False)
    
    # Paginação
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar não lidas
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
        'filter_type': filter_type,
        'filter_read': filter_read,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    
    log_user_action(request, request.user, 'view_notifications', 'notifications')
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, pk):
    """Marca uma notificação como lida"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    if request.method == 'POST':
        notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Notificação marcada como lida'})
        
        messages.success(request, 'Notificação marcada como lida.')
        
        # Redirect to event if exists
        if notification.event:
            return redirect('events:event_detail', pk=notification.event.pk)
        
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    """Marca todas as notificações como lidas"""
    if request.method == 'POST':
        unread_notifications = request.user.notifications.filter(is_read=False)
        count = unread_notifications.count()
        
        for notification in unread_notifications:
            notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'{count} notificações marcadas como lidas',
                'count': 0
            })
        
        messages.success(request, f'{count} notificações marcadas como lidas.')
        
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """Retorna o número de notificações não lidas (AJAX)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_recent_notifications(request):
    """Retorna notificações recentes (AJAX)"""
    notifications = request.user.notifications.filter(
        is_read=False
    ).order_by('-created_at')[:5]
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            'type': notification.get_notification_type_display(),
            'priority': notification.priority,
            'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
        })
    
    return JsonResponse({'notifications': data})


class NotificationPreferenceView(LoginRequiredMixin, UpdateView):
    """View para atualizar preferências de notificação"""
    model = NotificationPreference
    form_class = NotificationPreferenceForm
    template_name = 'notifications/preferences.html'
    success_url = reverse_lazy('notifications:preferences')
    
    def get_object(self, queryset=None):
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Preferências de notificação atualizadas com sucesso!')
        log_user_action(self.request, self.request.user, 'update_notification_preferences', 'preferences')
        return response


@login_required
def delete_notification(request, pk):
    """Exclui uma notificação"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    if request.method == 'POST':
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Notificação excluída'})
        
        messages.success(request, 'Notificação excluída.')
    
    return redirect('notifications:list')


@login_required
def notification_detail(request, pk):
    """Detalhe da notificação"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    # Marcar como lida automaticamente
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    
    return render(request, 'notifications/notification_detail.html', context)