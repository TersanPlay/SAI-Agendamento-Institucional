"""
Security middleware for enhanced access logging and security features
"""
import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve
from django.utils import timezone
from accounts.models import AccessLog
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para log de segurança e controle de acesso
    """
    
    # Actions that should be logged
    LOGGED_ACTIONS = {
        'GET': ['view', 'download', 'export'],
        'POST': ['create', 'login', 'register', 'generate'],
        'PUT': ['update', 'edit'],
        'PATCH': ['update', 'edit'],
        'DELETE': ['delete', 'remove'],
    }
    
    # Sensitive URLs that require special attention
    SENSITIVE_URLS = [
        'admin',
        'user_management',
        'monitoring_dashboard',
        'reports',
        'event_delete',
        'user_delete'
    ]
    
    def process_request(self, request):
        """Processa requisição de entrada"""
        request._start_time = time.time()
        
        # Rate limiting para usuários não autenticados
        if isinstance(request.user, AnonymousUser):
            ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{ip}"
            requests_count = cache.get(cache_key, 0)
            
            if requests_count > getattr(settings, 'RATE_LIMIT_ANONYMOUS', 100):
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return HttpResponse("Too many requests", status=429)
            
            cache.set(cache_key, requests_count + 1, 3600)  # 1 hour window
        
        return None
    
    def process_response(self, request, response):
        """Processa resposta de saída"""
        # Skip logging for static files and AJAX polling
        if self.should_skip_logging(request):
            return response
        
        # Log the access
        if not isinstance(request.user, AnonymousUser):
            self.log_access(request, response)
        
        return response
    
    def should_skip_logging(self, request):
        """Determina se deve pular o logging desta requisição"""
        path = request.path
        
        # Skip static files
        if any(path.startswith(prefix) for prefix in ['/static/', '/media/', '/favicon.ico']):
            return True
        
        # Skip frequent AJAX calls
        if 'notification' in path and request.method == 'GET':
            return True
        
        # Skip admin static files
        if '/admin/jsi18n/' in path:
            return True
            
        return False
    
    def log_access(self, request, response):
        """Registra o acesso no log de segurança"""
        try:
            # Determine action based on URL and method
            action = self.determine_action(request)
            resource = self.determine_resource(request)
            
            # Check if this is a sensitive operation
            is_sensitive = any(url in request.path for url in self.SENSITIVE_URLS)
            
            # Calculate execution time
            execution_time = None
            if hasattr(request, '_start_time'):
                execution_time = time.time() - request._start_time
            
            # Create access log entry
            AccessLog.objects.create(
                user=request.user,
                action=action,
                resource=resource,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                success=200 <= response.status_code < 400,
            )
            
            # Log sensitive operations
            if is_sensitive:
                logger.info(
                    f"Sensitive operation: {request.user.username} "
                    f"performed {action} on {resource} from IP {self.get_client_ip(request)}"
                )
            
            # Log slow requests
            if execution_time and execution_time > 5.0:
                logger.warning(
                    f"Slow request: {action} on {resource} took {execution_time:.2f}s "
                    f"for user {request.user.username}"
                )
                
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
    
    def determine_action(self, request):
        """Determina a ação baseada na URL e método"""
        method = request.method
        path = request.path
        
        try:
            url_name = resolve(path).url_name
        except:
            url_name = 'unknown'
        
        # Map URL patterns to actions
        if 'login' in path:
            return 'login'
        elif 'logout' in path:
            return 'logout'
        elif 'create' in path or 'add' in path:
            return 'create'
        elif 'edit' in path or 'update' in path:
            return 'edit'
        elif 'delete' in path:
            return 'delete'
        elif 'export' in path or 'download' in path:
            return 'export'
        elif 'dashboard' in path:
            return 'view_dashboard'
        elif 'calendar' in path:
            return 'view_calendar'
        elif 'reports' in path:
            return 'view_reports'
        elif method == 'POST':
            return 'submit'
        elif method in ['PUT', 'PATCH']:
            return 'update'
        elif method == 'DELETE':
            return 'delete'
        else:
            return 'view'
    
    def determine_resource(self, request):
        """Determina o recurso baseado na URL"""
        path = request.path
        
        if 'event' in path:
            return 'events'
        elif 'user' in path or 'account' in path:
            return 'users'
        elif 'notification' in path:
            return 'notifications'
        elif 'report' in path:
            return 'reports'
        elif 'dashboard' in path:
            return 'dashboard'
        elif 'calendar' in path:
            return 'calendar'
        elif 'admin' in path:
            return 'admin'
        else:
            return 'general'
    
    def get_client_ip(self, request):
        """Obtém o IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para adicionar cabeçalhos de segurança
    """
    
    def process_response(self, request, response):
        """Adiciona cabeçalhos de segurança"""
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        if not response.get('Content-Security-Policy'):
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
                "img-src 'self' data: https:",
                "font-src 'self' https://cdnjs.cloudflare.com",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "base-uri 'self'"
            ]
            response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Force HTTPS in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class BruteForceProtectionMiddleware(MiddlewareMixin):
    """
    Middleware para proteção contra ataques de força bruta
    """
    
    def process_request(self, request):
        """Verifica tentativas de login repetidas"""
        if request.path == '/accounts/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f"login_attempts_{ip}"
            attempts = cache.get(cache_key, 0)
            
            # Limit login attempts
            max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
            lockout_time = getattr(settings, 'LOGIN_LOCKOUT_TIME', 900)  # 15 minutes
            
            if attempts >= max_attempts:
                logger.warning(f"Login blocked for IP {ip} due to too many failed attempts")
                return HttpResponse(
                    "Too many login attempts. Please try again later.",
                    status=429
                )
        
        return None
    
    def process_response(self, request, response):
        """Processa resposta de login"""
        if request.path == '/accounts/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f"login_attempts_{ip}"
            
            if response.status_code == 302:  # Successful login redirect
                # Clear failed attempts on successful login
                cache.delete(cache_key)
            elif response.status_code == 200:  # Failed login (stays on login page)
                # Increment failed attempts
                attempts = cache.get(cache_key, 0) + 1
                lockout_time = getattr(settings, 'LOGIN_LOCKOUT_TIME', 900)
                cache.set(cache_key, attempts, lockout_time)
                
                logger.warning(f"Failed login attempt from IP {ip} (attempt {attempts})")
        
        return response
    
    def get_client_ip(self, request):
        """Obtém o IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip