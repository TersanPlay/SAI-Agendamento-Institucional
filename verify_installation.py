#!/usr/bin/env python
"""
Script de verificação da instalação do EventoSys
"""

import os
import sys
import django
from pathlib import Path

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    django.setup()
    print("✅ Django configurado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

def test_imports():
    """Testa se todos os modelos podem ser importados"""
    try:
        from events.models import Event, EventType, Department, Location
        from accounts.models import UserProfile, AccessLog
        from notifications.models import Notification
        from reports.models import Report
        print("✅ Todos os modelos importados com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}")
        return False

def test_database():
    """Testa a conexão com o banco de dados"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexão com banco de dados OK!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def test_urls():
    """Testa se as URLs estão configuradas"""
    try:
        from django.urls import reverse
        from django.test import RequestFactory
        
        # Testar algumas URLs básicas
        urls_to_test = [
            'events:home',
            'accounts:login',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ URL {url_name}: {url}")
            except Exception as e:
                print(f"❌ Erro na URL {url_name}: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar URLs: {e}")
        return False

def show_next_steps():
    """Mostra os próximos passos para usar o sistema"""
    print("\n" + "="*60)
    print("🚀 PRÓXIMOS PASSOS PARA USAR O EVENTOSYS:")
    print("="*60)
    print("1. Instalar dependências:")
    print("   pip install -r requirements.txt")
    print("\n2. Criar migrações:")
    print("   python manage.py makemigrations")
    print("\n3. Aplicar migrações:")
    print("   python manage.py migrate")
    print("\n4. Carregar dados iniciais:")
    print("   python manage.py populate_initial_data")
    print("\n5. Executar o servidor:")
    print("   python manage.py runserver")
    print("\n6. Acessar o sistema:")
    print("   http://127.0.0.1:8000")
    print("\n7. Fazer login com:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    print("="*60)

def main():
    print("🔍 VERIFICAÇÃO DA INSTALAÇÃO DO EVENTOSYS")
    print("="*50)
    
    # Executar testes
    tests = [
        ("Importação de modelos", test_imports),
        ("URLs do Django", test_urls),
    ]
    
    success_count = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Testando: {test_name}")
        if test_func():
            success_count += 1
    
    print(f"\n📊 RESULTADO: {success_count}/{len(tests)} testes passaram")
    
    if success_count == len(tests):
        print("🎉 Sistema configurado corretamente!")
        show_next_steps()
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")

if __name__ == "__main__":
    main()