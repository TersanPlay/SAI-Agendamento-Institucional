import random
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import EventType, Location, Department, Event, EventParticipant
from accounts.models import UserProfile
from reports.models import Report

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste para eventos, relatórios e calendários'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa os dados existentes antes de popular',
        )
    
    def handle(self, *args, **options):
        try:
            if options['clear']:
                self.stdout.write('Limpando dados de teste existentes...')
                self.clear_test_data()
            
            self.stdout.write('Iniciando população de dados de teste...')
            
            # 1. Criar usuários de teste
            self.create_test_users()
            
            # 2. Gerar eventos únicos
            self.generate_unique_events()
            
            # 3. Gerar eventos recorrentes
            self.generate_recurring_events()
            
            # 4. Gerar participantes e associações
            self.generate_participants()
            
            # 5. Gerar dados de relatórios
            self.generate_report_data()
            
            self.stdout.write(
                self.style.SUCCESS(  # type: ignore
                    'Dados de teste populados com sucesso!'
                )
            )
        except Exception as e:
            logger.error(f"Erro ao popular dados de teste: {str(e)}")
            self.stdout.write(
                self.style.ERROR(  # type: ignore
                    f'Erro ao popular dados de teste: {str(e)}'
                )
            )
    
    def clear_test_data(self):
        """Limpa os dados de teste existentes"""
        # Limpar eventos de teste (com nomes que começam com "Teste")
        Event.objects.filter(name__startswith='Teste').delete()  # type: ignore
        
        # Limpar relatórios de teste
        Report.objects.filter(name__startswith='Relatório Teste').delete()  # type: ignore
        
        # Limpar usuários de teste (exceto admin)
        User.objects.filter(username__startswith='test_').delete()  # type: ignore
        
        self.stdout.write('Dados de teste limpos com sucesso.')
    
    def create_test_users(self):
        """Cria usuários de teste para diferentes papéis"""
        departments = list(Department.objects.all())  # type: ignore
        user_types = ['administrador', 'gestor', 'visualizador']
        
        for i in range(10):
            username = f'test_user_{i}'
            if not User.objects.filter(username=username).exists():  # type: ignore
                user = User.objects.create_user(  # type: ignore
                    username=username,
                    email=f'test{i}@eventosys.com',
                    password='test123',
                    first_name=f'Usuário {i}',
                    last_name='Teste'
                )
                
                # Criar perfil do usuário
                UserProfile.objects.get_or_create(  # type: ignore
                    user=user,
                    defaults={
                        'user_type': random.choice(user_types),
                        'department': random.choice(departments) if departments else None,
                        'phone': f'(11) 9{i:04d}-{i:04d}',
                        'receive_notifications': random.choice([True, False])
                    }
                )
                
                self.stdout.write(f'Usuário de teste criado: {username}')
    
    def generate_unique_events(self):
        """Gera eventos únicos (passados, presentes e futuros)"""
        event_types = list(EventType.objects.all())  # type: ignore
        locations = list(Location.objects.all())  # type: ignore
        departments = list(Department.objects.all())  # type: ignore
        users = list(User.objects.all())  # type: ignore
        
        if not (event_types and locations and departments and users):
            self.stdout.write(
                self.style.WARNING(  # type: ignore
                    'Dados insuficientes para criar eventos. Certifique-se de ter tipos de eventos, locais, departamentos e usuários.'
                )
            )
            return
        
        # Gerar eventos para os últimos 3 meses e próximos 6 meses
        now = timezone.now()
        start_date = now - timedelta(days=90)  # 3 meses atrás
        end_date = now + timedelta(days=180)   # 6 meses à frente
        
        # Status possíveis
        statuses = ['planejado', 'em_andamento', 'concluido', 'cancelado']
        
        # Modalidades possíveis
        location_modes = ['presencial', 'virtual', 'hibrido']
        
        # Público-alvo possíveis
        target_audiences = ['publico_interno', 'publico_externo', 'ambos']
        
        # Gerar 50 eventos únicos
        for i in range(50):
            # Gerar data aleatória dentro do intervalo
            random_days = random.randint(0, (end_date - start_date).days)
            event_date = start_date + timedelta(days=random_days)
            
            # Definir horário aleatório entre 8h e 18h
            hour = random.randint(8, 17)
            minute = random.choice([0, 15, 30, 45])
            start_datetime = event_date.replace(hour=hour, minute=minute)
            end_datetime = start_datetime + timedelta(hours=random.choice([1, 2, 3, 4]))
            
            # Selecionar dados aleatórios
            event_type = random.choice(event_types)
            location_mode = random.choice(location_modes)
            location = random.choice(locations) if location_mode != 'virtual' else None
            department = random.choice(departments)
            responsible = random.choice(users)
            creator = random.choice(users)
            status = random.choice(statuses)
            target_audience = random.choice(target_audiences)
            
            # Criar evento
            event = Event.objects.create(  # type: ignore
                name=f'Teste Evento Único {i+1}',
                event_type=event_type,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location_mode=location_mode,
                location=location,
                virtual_link='https://meet.google.com/test-meeting' if location_mode in ['virtual', 'hibrido'] else '',
                target_audience=target_audience,
                responsible_person=responsible,
                department=department,
                status=status,
                description=f'Descrição do evento de teste único {i+1}. Este é um evento gerado automaticamente para testes.',
                observations=f'Observações do evento de teste {i+1}',
                created_by=creator,
                is_public=random.choice([True, False])
            )
            
            self.stdout.write(f'Evento único criado: {event.name} - {event.start_datetime.strftime("%d/%m/%Y %H:%M")}')
    
    def generate_recurring_events(self):
        """Gera eventos recorrentes (diários, semanais, mensais)"""
        event_types = list(EventType.objects.all())  # type: ignore
        locations = list(Location.objects.all())  # type: ignore
        departments = list(Department.objects.all())  # type: ignore
        users = list(User.objects.all())  # type: ignore
        
        if not (event_types and locations and departments and users):
            self.stdout.write(
                self.style.WARNING(  # type: ignore
                    'Dados insuficientes para criar eventos recorrentes.'
                )
            )
            return
        
        now = timezone.now()
        start_date = now - timedelta(days=30)  # Começar 1 mês atrás
        end_date = now + timedelta(days=90)    # Terminar 3 meses à frente
        
        # Tipos de recorrência
        recurrence_types = ['diário', 'semanal', 'mensal']
        statuses = ['planejado', 'em_andamento', 'concluido', 'cancelado']
        location_modes = ['presencial', 'virtual', 'hibrido']
        target_audiences = ['publico_interno', 'publico_externo', 'ambos']
        
        # Gerar 3 eventos recorrentes de cada tipo
        for recurrence_type in recurrence_types:
            for i in range(3):
                # Data inicial aleatória
                random_days = random.randint(0, 30)
                base_date = start_date + timedelta(days=random_days)
                
                # Horário fixo para eventos recorrentes
                hour = random.randint(9, 16)
                start_datetime = base_date.replace(hour=hour, minute=0)
                end_datetime = start_datetime + timedelta(hours=1)
                
                # Selecionar dados aleatórios
                event_type = random.choice(event_types)
                location_mode = random.choice(location_modes)
                location = random.choice(locations) if location_mode != 'virtual' else None
                department = random.choice(departments)
                responsible = random.choice(users)
                creator = random.choice(users)
                status = random.choice(statuses)
                target_audience = random.choice(target_audiences)
                
                # Criar evento recorrente base
                event = Event.objects.create(  # type: ignore
                    name=f'Teste Evento Recorrente {recurrence_type} {i+1}',
                    event_type=event_type,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location_mode=location_mode,
                    location=location,
                    virtual_link='https://meet.google.com/test-recurring' if location_mode in ['virtual', 'hibrido'] else '',
                    target_audience=target_audience,
                    responsible_person=responsible,
                    department=department,
                    status=status,
                    description=f'Descrição do evento recorrente {recurrence_type} {i+1}. Este é um evento gerado automaticamente para testes.',
                    observations=f'Observações do evento recorrente {i+1}',
                    created_by=creator,
                    is_public=True
                )
                
                self.stdout.write(f'Evento recorrente base criado: {event.name} - {recurrence_type}')
                
                # Criar instâncias recorrentes (5 instâncias para cada)
                for j in range(1, 6):
                    if recurrence_type == 'diário':
                        instance_date = start_datetime + timedelta(days=j)
                    elif recurrence_type == 'semanal':
                        instance_date = start_datetime + timedelta(weeks=j)
                    else:  # mensal
                        instance_date = start_datetime + timedelta(days=30*j)
                    
                    # Ajustar para não ultrapassar o limite final
                    if instance_date > end_date:
                        break
                    
                    instance_start = instance_date.replace(hour=hour, minute=0)
                    instance_end = instance_start + timedelta(hours=1)
                    
                    # Criar instância do evento recorrente
                    recurring_event = Event.objects.create(  # type: ignore
                        name=f'{event.name} - Instância {j}',
                        event_type=event_type,
                        start_datetime=instance_start,
                        end_datetime=instance_end,
                        location_mode=location_mode,
                        location=location,
                        virtual_link='https://meet.google.com/test-recurring' if location_mode in ['virtual', 'hibrido'] else '',
                        target_audience=target_audience,
                        responsible_person=responsible,
                        department=department,
                        status=random.choice(statuses),  # Status pode variar nas instâncias
                        description=f'Instância {j} do {event.name}',
                        observations=f'Instância {j} gerada automaticamente',
                        created_by=creator,
                        is_public=True
                    )
                    
                    self.stdout.write(f'  Instância criada: {recurring_event.name} - {instance_start.strftime("%d/%m/%Y %H:%M")}')
    
    def generate_participants(self):
        """Gera participantes e associações para os eventos"""
        events = list(Event.objects.filter(name__startswith='Teste'))  # type: ignore
        users = list(User.objects.filter(username__startswith='test_'))  # type: ignore
        
        if not (events and users):
            self.stdout.write(
                self.style.WARNING(  # type: ignore
                    'Dados insuficientes para criar participantes.'
                )
            )
            return
        
        # Para cada evento, adicionar entre 3 e 10 participantes
        for event in events:
            # Selecionar aleatoriamente entre 3 e 10 usuários
            num_participants = random.randint(3, min(10, len(users)))
            selected_users = random.sample(users, num_participants)
            
            for user in selected_users:
                # Criar participante
                participant, created = EventParticipant.objects.get_or_create(  # type: ignore
                    event=event,
                    user=user,
                    defaults={
                        'confirmed': random.choice([True, False]),
                        'attended': random.choice([True, False]) if event.is_past else False
                    }
                )
                
                if created:
                    self.stdout.write(f'Participante adicionado: {user.username} ao evento {event.name}')
        
        self.stdout.write('Participantes gerados com sucesso.')
    
    def generate_report_data(self):
        """Gera dados para relatórios"""
        departments = list(Department.objects.all())  # type: ignore
        event_types = list(EventType.objects.all())  # type: ignore
        users = list(User.objects.all())  # type: ignore
        
        if not (departments and event_types and users):
            self.stdout.write(
                self.style.WARNING(  # type: ignore
                    'Dados insuficientes para criar relatórios.'
                )
            )
            return
        
        now = timezone.now()
        
        # Tipos de relatórios
        report_types = [
            'events_by_period',
            'events_by_type',
            'events_by_department',
            'events_by_status',
            'participant_summary',
            'location_usage',
            'monthly_summary',
            'yearly_summary'
        ]
        
        formats = ['pdf', 'excel', 'csv']
        
        # Gerar 10 relatórios de teste
        for i in range(10):
            report_type = random.choice(report_types)
            creator = random.choice(users)
            format_choice = random.choice(formats)
            
            # Datas aleatórias nos últimos 6 meses
            start_date = now - timedelta(days=random.randint(30, 180))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            report = Report.objects.create(  # type: ignore
                name=f'Relatório Teste {i+1} - {report_type}',
                report_type=report_type,
                description=f'Relatório de teste do tipo {report_type} gerado automaticamente',
                start_date=start_date.date(),
                end_date=end_date.date(),
                format=format_choice,
                is_scheduled=random.choice([True, False]),
                schedule_frequency=random.choice(['daily', 'weekly', 'monthly']) if random.choice([True, False]) else '',
                created_by=creator
            )
            
            # Adicionar departamentos e tipos de evento aleatórios (opcional)
            if random.choice([True, False]) and departments:
                num_departments = random.randint(1, min(3, len(departments)))
                selected_departments = random.sample(departments, num_departments)
                report.departments.set(selected_departments)
            
            if random.choice([True, False]) and event_types:
                num_event_types = random.randint(1, min(5, len(event_types)))
                selected_event_types = random.sample(event_types, num_event_types)
                report.event_types.set(selected_event_types)
            
            self.stdout.write(f'Relatório criado: {report.name}')
        
        self.stdout.write('Dados de relatórios gerados com sucesso.')