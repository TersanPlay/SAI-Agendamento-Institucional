from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Envia notifica\u00e7\u00f5es de lembrete para eventos pr\u00f3ximos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem criar notifica\u00e7\u00f5es (apenas mostra o que seria feito)',
        )
        
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=30,
            help='N\u00famero de dias para manter notifica\u00e7\u00f5es antigas (padr\u00e3o: 30)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        cleanup_days = options['cleanup_days']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Iniciando processamento de notifica\u00e7\u00f5es - {timezone.now().strftime(\"%d/%m/%Y %H:%M:%S\")}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY RUN - nenhuma notifica\u00e7\u00e3o ser\u00e1 criada')
            )
        
        # Criar notifica\u00e7\u00f5es de lembrete
        if not dry_run:
            reminder_notifications = NotificationService.create_reminder_notifications()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Criadas {len(reminder_notifications)} notifica\u00e7\u00f5es de lembrete'
                )
            )
        else:
            self.stdout.write('Simulando cria\u00e7\u00e3o de notifica\u00e7\u00f5es de lembrete...')
        
        # Limpeza de notifica\u00e7\u00f5es antigas
        if not dry_run:
            deleted_count = NotificationService.cleanup_old_notifications(days=cleanup_days)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Removidas {deleted_count} notifica\u00e7\u00f5es antigas ({cleanup_days}+ dias)'
                )
            )
        else:
            self.stdout.write(f'Simulando limpeza de notifica\u00e7\u00f5es antigas ({cleanup_days}+ dias)...')
        
        self.stdout.write(
            self.style.SUCCESS('Processamento de notifica\u00e7\u00f5es conclu\u00eddo!')
        )", "original_text": "", "replace_all": false}]