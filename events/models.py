from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import uuid


class Department(models.Model):
    """Departamento responsável pelo evento"""
    name = models.CharField(max_length=100, verbose_name="Nome do Departamento")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['name']
    
    def __str__(self) -> str:
        return str(self.name)


class EventType(models.Model):
    """Tipos de eventos disponíveis no sistema"""
    EVENT_TYPES = [
        ('reuniao', 'Reunião'),
        ('audiencia_publica', 'Audiência Pública'),
        ('sessao_plenaria', 'Sessão Plenária'),
        ('palestra', 'Palestra'),
        ('workshop', 'Workshop'),
        ('seminario', 'Seminário'),
        ('congresso', 'Congresso'),
        ('curso_capacitacao', 'Curso/Capacitação'),
        ('mesa_redonda', 'Mesa-Redonda'),
        ('debate', 'Debate'),
        ('conferencia', 'Conferência'),
        ('encontro_tematico', 'Encontro Temático'),
        ('assembleia', 'Assembleia'),
        ('visita_tecnica', 'Visita Técnica'),
        ('cerimonia_oficial', 'Cerimônia Oficial'),
        ('lancamento_projeto', 'Lançamento de Projeto/Programa'),
        ('coletiva_imprensa', 'Coletiva de Imprensa'),
        ('atividade_cultural', 'Atividade Cultural'),
        ('atividade_comunitaria', 'Atividade Comunitária'),
        ('outros', 'Outros'),
    ]
    
    name = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Tipo")
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name="Cor", help_text="Código hex da cor (#RRGGBB)")
    icon = models.CharField(max_length=50, default='fas fa-calendar', verbose_name="Ícone", help_text="Classe do ícone FontAwesome")
    
    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"
        ordering = ['name']
    
    def __str__(self) -> str:
        # Using getattr to avoid static analysis issues
        get_display = getattr(self, 'get_name_display', None)
        if get_display:
            return str(get_display())
        return str(self.name)


class Location(models.Model):
    """Localizações disponíveis para eventos"""
    LOCATION_TYPES = [
        ('auditorio', 'Auditório'),
        ('plenarinho', 'Plenarinho'),
        ('presidencia', 'Presidência'),
        ('gabinete', 'Gabinete'),
        ('estacionamento_interno', 'Estacionamento Interno'),
        ('estacionamento_externo', 'Estacionamento Externo'),
        ('estacionamento_ambos', 'Estacionamento (Interno e Externo)'),
        ('virtual', 'Virtual'),
        ('outros', 'Outros'),
    ]
    
    name = models.CharField(max_length=50, choices=LOCATION_TYPES, verbose_name="Localização")
    custom_name = models.CharField(max_length=100, blank=True, verbose_name="Nome Personalizado", 
                                 help_text="Para gabinetes ou locais específicos")
    capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Capacidade")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"
        ordering = ['name']
    
    def __str__(self) -> str:
        # Using getattr to avoid static analysis issues
        get_display = getattr(self, 'get_name_display', None)
        if get_display:
            name_display = str(get_display())
        else:
            name_display = str(self.name)
            
        if self.custom_name:
            return f"{name_display} - {self.custom_name}"
        return name_display


class Event(models.Model):
    """Modelo principal para eventos institucionais"""
    
    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    LOCATION_MODE_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrido', 'Híbrido'),
    ]
    
    TARGET_AUDIENCE_CHOICES = [
        ('publico_interno', 'Público Interno'),
        ('publico_externo', 'Público Externo'),
        ('ambos', 'Ambos'),
    ]
    
    # Campos obrigatórios
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome do Evento")
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT, verbose_name="Tipo de Evento")
    
    # Data e horário
    start_datetime = models.DateTimeField(verbose_name="Data e Hora de Início")
    end_datetime = models.DateTimeField(verbose_name="Data e Hora de Término")
    
    # Local e localização
    location_mode = models.CharField(max_length=20, choices=LOCATION_MODE_CHOICES, verbose_name="Modalidade do Evento")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name="Localização", 
                               null=True, blank=True)
    virtual_link = models.URLField(blank=True, verbose_name="Link Virtual", 
                                 help_text="Para eventos virtuais ou híbridos")
    
    # Público e responsabilidade
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE_CHOICES, verbose_name="Público-alvo")
    responsible_person = models.ForeignKey(User, on_delete=models.PROTECT, 
                                         related_name='responsible_events', verbose_name="Responsável do Evento")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Departamento Responsável")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejado', verbose_name="Status")
    
    # Descrição e observações
    description = models.TextField(blank=True, verbose_name="Descrição")
    observations = models.TextField(blank=True, verbose_name="Observações")
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, 
                                 related_name='created_events', verbose_name="Criado por")
    
    # Campos de visibilidade
    is_public = models.BooleanField(default=False, verbose_name="Evento Público", help_text="Visível na área pública do sistema")  # type: ignore
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['event_type']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"  # type: ignore
    
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})
    
    @property
    def is_past(self):
        """Verifica se o evento já passou"""
        return self.end_datetime < timezone.now()
    
    @property
    def is_current(self):
        """Verifica se o evento está acontecendo agora"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime
    
    @property
    def duration_hours(self):
        """Calcula a duração do evento em horas"""
        duration = self.end_datetime - self.start_datetime  # type: ignore
        return duration.total_seconds() / 3600  # type: ignore
    
    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError("A data de início deve ser anterior à data de término.")
        
        if self.location_mode == 'virtual' and not self.virtual_link:
            raise ValidationError("Link virtual é obrigatório para eventos virtuais.")


class EventDocument(models.Model):
    """Termos de responsabilidade e documentos anexos ao evento"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100, verbose_name="Título do Documento")
    external_link = models.URLField(verbose_name="Link Externo")
    uploaded_file = models.FileField(upload_to='event_documents/', blank=True, 
                                   verbose_name="Arquivo (opcional)")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Documento do Evento"
        verbose_name_plural = "Documentos dos Eventos"
    
    def __str__(self) -> str:
        return f"{self.event.name} - {self.title}"


class EventHistory(models.Model):
    """Histórico de alterações dos eventos (versionamento)"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='history')
    field_name = models.CharField(max_length=50, verbose_name="Campo Alterado")
    old_value = models.TextField(verbose_name="Valor Anterior")
    new_value = models.TextField(verbose_name="Novo Valor")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Data da Alteração")
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Alterado por")
    
    class Meta:
        verbose_name = "Histórico do Evento"
        verbose_name_plural = "Histórico dos Eventos"
        ordering = ['-changed_at']
    
    def __str__(self) -> str:
        return f"{self.event.name} - {self.field_name} - {self.changed_at.strftime('%d/%m/%Y %H:%M')}"  # type: ignore


class EventParticipant(models.Model):
    """Participantes dos eventos"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Nome", 
                          help_text="Para participantes externos")
    email = models.EmailField(blank=True, verbose_name="Email")
    confirmed = models.BooleanField(default=False, verbose_name="Confirmado")  # type: ignore
    attended = models.BooleanField(default=False, verbose_name="Compareceu")  # type: ignore
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        unique_together = ['event', 'user']
    
    def __str__(self):
        if self.user:
            # Using getattr to avoid static analysis issues with ForeignKey attributes
            user_full_name = getattr(self.user, 'get_full_name', lambda: '')()
            user_username = getattr(self.user, 'username', '')
            return f"{self.event.name} - {user_full_name or user_username}"
        return f"{self.event.name} - {self.name}"