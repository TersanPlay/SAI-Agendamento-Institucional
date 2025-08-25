from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import EventType, Location, Department
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'
    
    def handle(self, *args, **options):
        # Criar tipos de eventos
        event_types_data = [
            ('reuniao', '#3B82F6', 'fas fa-users'),
            ('audiencia_publica', '#10B981', 'fas fa-gavel'),
            ('sessao_plenaria', '#8B5CF6', 'fas fa-landmark'),
            ('palestra', '#F59E0B', 'fas fa-chalkboard-teacher'),
            ('workshop', '#EF4444', 'fas fa-tools'),
            ('seminario', '#06B6D4', 'fas fa-graduation-cap'),
            ('congresso', '#84CC16', 'fas fa-handshake'),
            ('curso_capacitacao', '#F97316', 'fas fa-certificate'),
            ('mesa_redonda', '#EC4899', 'fas fa-comments'),
            ('debate', '#6B7280', 'fas fa-balance-scale'),
            ('conferencia', '#14B8A6', 'fas fa-microphone'),
            ('encontro_tematico', '#8B5CF6', 'fas fa-users-cog'),
            ('assembleia', '#DC2626', 'fas fa-gavel'),
            ('visita_tecnica', '#059669', 'fas fa-route'),
            ('cerimonia_oficial', '#7C3AED', 'fas fa-medal'),
            ('lancamento_projeto', '#0EA5E9', 'fas fa-rocket'),
            ('coletiva_imprensa', '#EA580C', 'fas fa-newspaper'),
            ('atividade_cultural', '#DB2777', 'fas fa-palette'),
            ('atividade_comunitaria', '#65A30D', 'fas fa-heart'),
            ('outros', '#6B7280', 'fas fa-ellipsis-h'),
        ]
        
        for name, color, icon in event_types_data:
            event_type, created = EventType.objects.get_or_create(  # type: ignore
                name=name,
                defaults={'color': color, 'icon': icon}
            )
            if created:
                self.stdout.write(f'Tipo de evento criado: {event_type.get_name_display()}')
        
        # Criar localizações
        locations_data = [
            ('auditorio', 'Auditório Principal', 200),
            ('plenarinho', 'Plenarinho', 50),
            ('presidencia', 'Presidência', 20),
            ('gabinete', 'Gabinete', 10),
            ('estacionamento_interno', 'Estacionamento Interno', None),
            ('estacionamento_externo', 'Estacionamento Externo', None),
            ('estacionamento_ambos', 'Estacionamento (Interno e Externo)', None),
            ('virtual', 'Virtual/Online', None),
            ('outros', 'Outros Locais', None),
        ]
        
        for name, custom_name, capacity in locations_data:
            location, created = Location.objects.get_or_create(  # type: ignore
                name=name,
                defaults={'custom_name': custom_name, 'capacity': capacity}
            )
            if created:
                self.stdout.write(f'Localização criada: {location}')
        
        # Criar departamentos
        departments_data = [
            ('Presidência', 'Gabinete da Presidência'),
            ('Secretaria Geral', 'Secretaria Geral da Instituição'),
            ('Departamento de Comunicação', 'Comunicação e Marketing'),
            ('Departamento Jurídico', 'Assessoria Jurídica'),
            ('Departamento de TI', 'Tecnologia da Informação'),
            ('Recursos Humanos', 'Gestão de Pessoas'),
            ('Assessoria de Imprensa', 'Comunicação Externa'),
            ('Departamento Administrativo', 'Administração Geral'),
        ]
        
        for name, description in departments_data:
            department, created = Department.objects.get_or_create(  # type: ignore
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Departamento criado: {department.name}')
        
        # Criar usuário administrador se não existir
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@eventosys.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            
            # Criar perfil do administrador
            profile, created = UserProfile.objects.get_or_create(  # type: ignore
                user=admin_user,
                defaults={
                    'user_type': 'administrador',
                    'department': Department.objects.first()  # type: ignore
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(  # type: ignore
                    'Usuário administrador criado: admin / admin123'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(  # type: ignore
                'Dados iniciais carregados com sucesso!'
            )
        )