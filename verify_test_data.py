#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

from events.models import Event
from reports.models import Report
from accounts.models import UserProfile
from django.contrib.auth.models import User

def verify_test_data():
    print("=== VERIFICAÇÃO DOS DADOS DE TESTE ===\n")
    
    # Verificar usuários
    total_users = User.objects.count()
    test_users = User.objects.filter(username__startswith='test_').count()
    print(f"Total de usuários: {total_users}")
    print(f"Usuários de teste: {test_users}")
    
    # Verificar eventos
    total_events = Event.objects.count()
    test_events = Event.objects.filter(name__startswith='Teste').count()
    print(f"\nTotal de eventos: {total_events}")
    print(f"Eventos de teste: {test_events}")
    
    # Mostrar alguns exemplos de eventos
    print("\nExemplos de eventos de teste:")
    events = Event.objects.filter(name__startswith='Teste')[:5]
    for event in events:
        print(f"  - {event.name}")
        print(f"    Data: {event.start_datetime.strftime('%d/%m/%Y %H:%M')}")
        print(f"    Status: {event.get_status_display()}")
        print(f"    Tipo: {event.event_type.get_name_display()}")
        print()
    
    # Verificar relatórios
    total_reports = Report.objects.count()
    test_reports = Report.objects.filter(name__startswith='Relatório Teste').count()
    print(f"Total de relatórios: {total_reports}")
    print(f"Relatórios de teste: {test_reports}")
    
    # Mostrar alguns exemplos de relatórios
    print("\nExemplos de relatórios de teste:")
    reports = Report.objects.filter(name__startswith='Relatório Teste')[:3]
    for report in reports:
        print(f"  - {report.name}")
        print(f"    Tipo: {report.get_report_type_display()}")
        print(f"    Formato: {report.get_format_display()}")
        print(f"    Período: {report.start_date} a {report.end_date}")
        print()
    
    # Participants functionality has been removed from the system
    print("\nParticipants functionality has been removed from the system.")

if __name__ == "__main__":
    verify_test_data()