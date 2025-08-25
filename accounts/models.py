from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Perfil estendido do usuário com controle de acesso"""
    
    USER_TYPES = [
        ('administrador', 'Administrador'),
        ('gestor', 'Gestor'),
        ('visualizador', 'Visualizador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='visualizador', 
                               verbose_name="Tipo de Usuário")
    department = models.ForeignKey('events.Department', on_delete=models.SET_NULL, 
                                 null=True, blank=True, verbose_name="Departamento")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name="Foto do Perfil")
    
    # Preferências
    receive_notifications = models.BooleanField(default=True, verbose_name="Receber Notificações")  # type: ignore
    
    calendar_view_preference = models.CharField(
        max_length=10, 
        choices=[('month', 'Mensal'), ('week', 'Semanal'), ('day', 'Diário'), ('list', 'Lista')],
        default='month',
        verbose_name="Visualização Preferida do Calendário"
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"
    
    def __str__(self):
        # Type checking fix: explicitly get the user object
        user_obj = self.user
        return f"{user_obj.get_full_name() or user_obj.username} ({self.get_user_type_display()})"  # type: ignore
    
    @property
    def is_administrator(self):
        return self.user_type == 'administrador'
    
    @property
    def is_manager(self):
        return self.user_type == 'gestor'
    
    @property
    def is_viewer(self):
        return self.user_type == 'visualizador'
    
    def can_create_events(self):
        """Administradores e gestores podem criar eventos"""
        return self.user_type in ['administrador', 'gestor']
    
    def can_edit_all_events(self):
        """Apenas administradores podem editar todos os eventos"""
        return self.user_type == 'administrador'
    
    def can_view_all_events(self):
        """Administradores podem ver todos os eventos, gestores veem do seu departamento"""
        return self.user_type in ['administrador', 'gestor']
    
    def can_view_reports(self):
        """Administradores e gestores podem ver relatórios"""
        return self.user_type in ['administrador', 'gestor']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)  # type: ignore


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class AccessLog(models.Model):
    """Log de acessos para auditoria"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, verbose_name="Ação")
    resource = models.CharField(max_length=100, verbose_name="Recurso")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    user_agent = models.TextField(verbose_name="User Agent")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    success = models.BooleanField(default=True, verbose_name="Sucesso")  # type: ignore
    
    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"  # type: ignore