from django.http import HttpRequest
from django.contrib.auth.models import User
from django.db import models
from .models import AccessLog
import logging

logger = logging.getLogger('accounts')

# Manager reference for easier access (using getattr to avoid type checking issues)
access_log_manager = getattr(AccessLog, 'objects')


def get_client_ip(request: HttpRequest) -> str:
    """Obtém o IP do cliente da requisição"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_user_agent(request: HttpRequest) -> str:
    """Obtém o User Agent da requisição"""
    return request.META.get('HTTP_USER_AGENT', '')


def log_user_action(request: HttpRequest, user: User, action: str, resource: str, success: bool = True):
    """Registra uma ação do usuário no log de auditoria"""
    try:
        access_log_manager.create(
            user=user,
            action=action,
            resource=resource,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=success
        )
        logger.info(f"User {user.username} performed {action} on {resource}")
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")


def has_permission(user: User, permission_type: str, resource=None) -> bool:
    """Verifica se o usuário tem permissão para realizar uma ação"""
    if not user.is_authenticated:
        return False
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    
    # Administradores têm acesso total
    if profile.is_administrator:
        return True
    
    # Mapeamento de permissões
    permissions = {
        'create_event': profile.user_type in ['administrador', 'gestor'],
        'edit_all_events': profile.user_type == 'administrador',
        'view_all_events': profile.user_type in ['administrador', 'gestor'],
        'manage_users': profile.is_administrator,
        'view_reports': profile.user_type in ['administrador', 'gestor'],
        'add_report': profile.user_type in ['administrador', 'gestor'],
        'generate_reports': profile.user_type in ['administrador', 'gestor'],
        'view_access_logs': profile.is_administrator,
        'manage_departments': profile.is_administrator,
    }
    
    return permissions.get(permission_type, False)


def can_edit_event(user: User, event) -> bool:
    """Verifica se o usuário pode editar um evento específico"""
    if not user.is_authenticated:
        return False
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    
    # Administradores podem editar qualquer evento
    if profile.is_administrator:
        return True
    
    # Gestores podem editar eventos do seu departamento ou eventos que criaram
    if profile.is_manager:
        return (event.department == profile.department or 
                event.created_by == user or 
                event.responsible_person == user)
    
    # Visualizadores só podem editar eventos que criaram (se tiverem permissão)
    if profile.is_viewer:
        return event.created_by == user
    
    return False


def can_view_event(user: User, event) -> bool:
    """Verifica se o usuário pode visualizar um evento específico"""
    if not user.is_authenticated:
        return event.is_public  # Eventos públicos podem ser vistos por não autenticados
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return event.is_public
    
    # Administradores podem ver qualquer evento
    if profile.is_administrator:
        return True
    
    # Gestores podem ver eventos do seu departamento
    if profile.is_manager:
        return (event.department == profile.department or 
                event.is_public or
                event.created_by == user or
                event.responsible_person == user)
    
    # Visualizadores podem ver eventos públicos e eventos onde são responsáveis
    if profile.is_viewer:
        return (event.is_public or 
                event.created_by == user or
                event.responsible_person == user)
    
    return False


def get_user_accessible_events(user: User):
    """Retorna queryset de eventos que o usuário pode acessar"""
    from events.models import Event
    from django.db.models import Q
    
    if not user.is_authenticated:
        return getattr(Event, 'objects').filter(is_public=True)
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return getattr(Event, 'objects').filter(is_public=True)
    
    # Administradores veem todos os eventos
    if profile.is_administrator:
        return getattr(Event, 'objects').all()
    
    # Gestores veem eventos do departamento
    if profile.is_manager:
        q_objects = Q(department=profile.department)
        q_objects.add(Q(is_public=True), Q.OR)
        q_objects.add(Q(created_by=user), Q.OR)
        q_objects.add(Q(responsible_person=user), Q.OR)
        return getattr(Event, 'objects').filter(q_objects).distinct()
    
    # Visualizadores veem eventos públicos e onde são responsáveis
    if profile.is_viewer:
        q_objects = Q(is_public=True)
        q_objects.add(Q(created_by=user), Q.OR)
        q_objects.add(Q(responsible_person=user), Q.OR)
        return getattr(Event, 'objects').filter(q_objects).distinct()
    
    return getattr(Event, 'objects').filter(is_public=True)
