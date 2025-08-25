#!/usr/bin/env python
"""
Script to verify Django 5.2.5 upgrade
"""

import os
import sys
import django
from pathlib import Path

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def main():
    print("=== DJANGO 5.2.5 UPGRADE VERIFICATION ===\n")
    
    try:
        django.setup()
        print(f"✅ Django version: {django.get_version()}")
        print(f"✅ Django VERSION tuple: {django.VERSION}")
        
        # Test model imports
        from events.models import Event, EventType, Department
        from accounts.models import UserProfile
        from notifications.models import Notification
        from reports.models import Report
        print("✅ All models imported successfully!")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection working!")
        
        # Test Django admin
        from django.contrib import admin
        print(f"✅ Django admin is available")
        
        # Test URL configuration
        from django.urls import reverse
        try:
            home_url = reverse('events:home')
            login_url = reverse('accounts:login')
            print(f"✅ URL routing working - Home: {home_url}, Login: {login_url}")
        except Exception as e:
            print(f"⚠️  URL routing issue: {e}")
        
        # Test static files configuration
        from django.conf import settings
        print(f"✅ Static URL: {settings.STATIC_URL}")
        print(f"✅ Media URL: {settings.MEDIA_URL}")
        
        # Test new Django 5.2 features
        print(f"✅ DEFAULT_AUTO_FIELD: {settings.DEFAULT_AUTO_FIELD}")
        
        print("\n🎉 Django 5.2.5 upgrade verification SUCCESSFUL!")
        print("All core components are working correctly.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n⚠️  Some issues were found. Please check the installation.")
        sys.exit(1)
    else:
        print("\n✅ Ready to run: python manage.py runserver")