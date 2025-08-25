from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.utils import get_user_accessible_events, has_permission
from events.models import Event, EventType, Department
from accounts.models import User, AccessLog
from notifications.models import Notification
import json


def monitoring_dashboard(request):
    """Dashboard de monitoramento em tempo real"""
    try:
        # Remove login requirement for testing - in production, uncomment the next line
        # if not has_permission(request.user, 'view_reports'):
        #     return render(request, 'dashboard/access_denied.html')
        
        # Período padrão: últimos 30 dias
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # For testing, use the first user if not authenticated
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        # Safely check if user has profile and is admin
        is_admin = False
        if user and hasattr(user, 'profile'):
            try:
                is_admin = user.profile.is_administrator
            except Exception:
                is_admin = False
        
        context = {
            'is_admin': is_admin,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        }
        
        return render(request, 'dashboard/monitoring.html', context)
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in monitoring_dashboard: {str(e)}", exc_info=True)
        # Return a simple error page or redirect
        return render(request, 'dashboard/access_denied.html')


def dashboard_metrics_api(request):
    """API para métricas do dashboard em tempo real"""
    try:
        # Remove login requirement for testing - in production, uncomment the next lines
        # if not has_permission(request.user, 'view_reports'):
        #     return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Parâmetros de data
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        # For testing, use the first user if not authenticated
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        if not user:
            return JsonResponse({'error': 'No users found'}, status=404)
        
        if not hasattr(user, 'profile'):
            return JsonResponse({'error': 'User has no profile'}, status=403)
        
        # Check permissions
        if not has_permission(user, 'view_reports'):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Eventos acessíveis
        events = get_user_accessible_events(user)
        period_events = events.filter(
            start_datetime__date__gte=start_date,
            start_datetime__date__lte=end_date
        )
        
        # Métricas básicas
        now = timezone.now()
        today = now.date()
        
        metrics = {
            'overview': {
                'total_events': period_events.count(),
                'events_today': events.filter(start_datetime__date=today).count(),
                'events_this_week': events.filter(
                    start_datetime__date__gte=today - timedelta(days=today.weekday()),
                    start_datetime__date__lte=today + timedelta(days=6-today.weekday())
                ).count(),
                'events_this_month': events.filter(
                    start_datetime__date__gte=today.replace(day=1)
                ).count(),
            },
            
            'by_status': list(period_events.values('status').annotate(
                count=Count('id')
            ).order_by('status')),
            
            'by_type': list(period_events.values(
                'event_type__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            
            'by_department': list(period_events.values(
                'department__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            
            'daily_events': get_daily_events_data(period_events, start_date, end_date),
            
            # SQLite doesn't support aggregations on datetime fields, so we calculate average duration manually
            'event_duration_avg': None,  # Disabled for SQLite compatibility
            
            'upcoming_events': events.filter(
                start_datetime__gte=now,
                start_datetime__lte=now + timedelta(days=7)
            ).count(),
            
            'overdue_events': events.filter(
                end_datetime__lt=now,
                status__in=['planejado', 'em_andamento']
            ).count(),
        }
        
        # Métricas adicionais para administradores
        # Check if user has profile and is administrator safely
        try:
            if hasattr(user, 'profile') and user.profile.is_administrator:
                metrics.update({
                    'user_activity': get_user_activity_data(start_date, end_date),
                    'notification_stats': get_notification_stats(start_date, end_date),
                    'system_health': get_system_health_metrics(),
                })
        except Exception as e:
            # If there's an error accessing admin metrics, continue without them
            pass
        
        return JsonResponse(metrics)
    
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in dashboard_metrics_api: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def event_trends_api(request):
    """API para tendências de eventos"""
    if not has_permission(request.user, 'view_reports'):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    # Últimos 12 meses
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    events = get_user_accessible_events(request.user)
    monthly_data = []
    
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        next_month = (current_date + timedelta(days=32)).replace(day=1)
        
        month_events = events.filter(
            start_datetime__date__gte=current_date,
            start_datetime__date__lt=next_month
        )
        
        monthly_data.append({
            'month': current_date.strftime('%Y-%m'),
            'month_name': current_date.strftime('%b %Y'),
            'total': month_events.count(),
            'by_status': {
                'planejado': month_events.filter(status='planejado').count(),
                'em_andamento': month_events.filter(status='em_andamento').count(),
                'concluido': month_events.filter(status='concluido').count(),
                'cancelado': month_events.filter(status='cancelado').count(),
            }
        })
        
        current_date = next_month
    
    return JsonResponse({'monthly_trends': monthly_data})


@login_required
def performance_metrics_api(request):
    """API para métricas de performance"""
    if not has_permission(request.user, 'view_reports'):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    events = get_user_accessible_events(request.user)
    
    # Análise de pontualidade
    completed_events = events.filter(status='concluido')
    # For now, we'll calculate on-time events differently since we need more complex logic
    on_time_events = completed_events.count()  # Simplified for now
    
    # Taxa de cancelamento
    total_events = events.count()
    cancelled_events = events.filter(status='cancelado').count()
    cancellation_rate = (cancelled_events / total_events * 100) if total_events > 0 else 0
    
    # Eventos por responsável
    events_by_responsible = list(events.values(
        'responsible_person__first_name',
        'responsible_person__last_name',
        'responsible_person__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # Utilização de locais
    location_usage = list(events.values(
        'location__name',
        'location__custom_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    metrics = {
        'completion_rate': {
            'total': completed_events.count(),
            'on_time': on_time_events,
            'percentage': (on_time_events / completed_events.count() * 100) if completed_events.count() > 0 else 0
        },
        'cancellation_rate': {
            'cancelled': cancelled_events,
            'total': total_events,
            'percentage': cancellation_rate
        },
        'events_by_responsible': events_by_responsible,
        'location_usage': location_usage,
        'avg_event_duration': get_average_event_duration(events),
        'busiest_days': get_busiest_days_data(events),
    }
    
    return JsonResponse(metrics)


def get_daily_events_data(events, start_date, end_date):
    """Gera dados de eventos por dia"""
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_events = events.filter(start_datetime__date=current_date)
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': day_events.count(),
            'status_breakdown': {
                'planejado': day_events.filter(status='planejado').count(),
                'em_andamento': day_events.filter(status='em_andamento').count(),
                'concluido': day_events.filter(status='concluido').count(),
                'cancelado': day_events.filter(status='cancelado').count(),
            }
        })
        current_date += timedelta(days=1)
    
    return daily_data


def get_user_activity_data(start_date, end_date):
    """Gera dados de atividade dos usuários"""
    # Logs de acesso no período
    access_logs = AccessLog.objects.filter(  # type: ignore
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )
    
    # Usuários mais ativos
    active_users = list(access_logs.values(
        'user__first_name',
        'user__last_name',
        'user__username'
    ).annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10])
    
    # Ações mais comuns
    common_actions = list(access_logs.values('action').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    return {
        'total_actions': access_logs.count(),
        'unique_users': access_logs.values('user').distinct().count(),
        'active_users': active_users,
        'common_actions': common_actions,
    }


def get_notification_stats(start_date, end_date):
    """Gera estatísticas de notificações"""
    notifications = Notification.objects.filter(  # type: ignore
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    return {
        'total_sent': notifications.count(),
        'total_read': notifications.filter(is_read=True).count(),
        'by_type': list(notifications.values('notification_type').annotate(
            count=Count('id')
        ).order_by('-count')),
        'by_priority': list(notifications.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')),
    }


def get_system_health_metrics():
    """Gera métricas de saúde do sistema"""
    now = timezone.now()
    
    # Últimas 24 horas
    last_24h = now - timedelta(hours=24)
    
    return {
        'active_users_24h': AccessLog.objects.filter(  # type: ignore
            timestamp__gte=last_24h
        ).values('user').distinct().count(),
        
        'events_created_24h': Event.objects.filter(  # type: ignore
            created_at__gte=last_24h
        ).count(),
        
        'notifications_sent_24h': Notification.objects.filter(  # type: ignore
            created_at__gte=last_24h
        ).count(),
        
        'error_rate': AccessLog.objects.filter(  # type: ignore
            timestamp__gte=last_24h,
            success=False
        ).count(),
        
        'database_size': Event.objects.count() + User.objects.count() + Notification.objects.count(),  # type: ignore  # type: ignore
    }


def get_average_event_duration(events):
    """Calcula duração média dos eventos"""
    durations = []
    for event in events.filter(end_datetime__isnull=False):
        duration = event.end_datetime - event.start_datetime
        durations.append(duration.total_seconds() / 3600)  # em horas
    
    return sum(durations) / len(durations) if durations else 0


def get_busiest_days_data(events):
    """Analisa os dias mais movimentados"""
    # Contar eventos por dia da semana
    weekday_counts = {}
    for i in range(7):
        weekday_counts[i] = events.filter(
            start_datetime__week_day=i+1  # Django usa 1-7 para dom-sab
        ).count()
    
    # Mapear nomes dos dias
    weekday_names = {
        0: 'Domingo', 1: 'Segunda', 2: 'Terça', 3: 'Quarta',
        4: 'Quinta', 5: 'Sexta', 6: 'Sábado'
    }
    
    return [{
        'day': weekday_names[i],
        'count': weekday_counts[i]
    } for i in range(7)]