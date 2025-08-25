from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Dashboard(models.Model):
    """Configuração de dashboards personalizados"""
    name = models.CharField(max_length=100, verbose_name="Nome do Dashboard")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    
    # Widgets habilitados
    show_events_today = models.BooleanField(default=True, verbose_name="Eventos de Hoje")  # type: ignore
    show_events_week = models.BooleanField(default=True, verbose_name="Eventos da Semana")  # type: ignore
    show_events_by_type = models.BooleanField(default=True, verbose_name="Eventos por Tipo")  # type: ignore
    show_events_by_status = models.BooleanField(default=True, verbose_name="Eventos por Status")  # type: ignore
    show_recent_activity = models.BooleanField(default=True, verbose_name="Atividade Recente")  # type: ignore
    show_my_events = models.BooleanField(default=True, verbose_name="Meus Eventos")  # type: ignore
    
    # Configurações de período padrão
    default_period_days = models.PositiveIntegerField(default=30, verbose_name="Período Padrão (dias)")
    
    is_default = models.BooleanField(default=False, verbose_name="Dashboard Padrão")  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Report(models.Model):
    """Relatórios automatizados do sistema"""
    
    REPORT_TYPES = [
        ('events_by_period', 'Eventos por Período'),
        ('events_by_type', 'Eventos por Tipo'),
        ('events_by_department', 'Eventos por Departamento'),
        ('events_by_status', 'Eventos por Status'),
        ('participant_summary', 'Resumo de Participantes'),
        ('location_usage', 'Uso de Localizações'),
        ('monthly_summary', 'Resumo Mensal'),
        ('yearly_summary', 'Resumo Anual'),
        ('custom', 'Relatório Personalizado'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nome do Relatório")
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, verbose_name="Tipo de Relatório")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Parâmetros do relatório
    start_date = models.DateField(verbose_name="Data Início")
    end_date = models.DateField(verbose_name="Data Fim")
    departments = models.ManyToManyField('events.Department', blank=True, verbose_name="Departamentos")
    event_types = models.ManyToManyField('events.EventType', blank=True, verbose_name="Tipos de Evento")
    
    # Configurações
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf', verbose_name="Formato")
    is_scheduled = models.BooleanField(default=False, verbose_name="Relatório Agendado")  # type: ignore
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Diário'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensal'),
            ('quarterly', 'Trimestral'),
            ('yearly', 'Anual'),
        ],
        blank=True,
        verbose_name="Frequência"
    )
    
    # Metadados
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    last_generated = models.DateTimeField(null=True, blank=True, verbose_name="Última Geração")
    
    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"
    
    def generate_file_name(self):
        """Gera nome do arquivo baseado no relatório"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        clean_name = self.name.replace(' ', '_').lower()
        return f"{clean_name}_{timestamp}.{self.format}"


class ReportExecution(models.Model):
    """Histórico de execuções de relatórios"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Executado por")
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name="Executado em")
    
    # Resultados
    success = models.BooleanField(default=True, verbose_name="Sucesso")  # type: ignore
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    file_path = models.FileField(upload_to='reports/', blank=True, verbose_name="Arquivo Gerado")
    records_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total de Registros")
    
    # Performance
    execution_time = models.FloatField(null=True, blank=True, verbose_name="Tempo de Execução (s)")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamanho do Arquivo (bytes)")
    
    class Meta:
        verbose_name = "Execução de Relatório"
        verbose_name_plural = "Execuções de Relatórios"
        ordering = ['-executed_at']
    
    def __str__(self):
        status = "Sucesso" if self.success else "Erro"
        return f"{self.report.name} - {status} - {self.executed_at.strftime('%d/%m/%Y %H:%M')}"

