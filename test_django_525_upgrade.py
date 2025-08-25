#!/usr/bin/env python
"""
Test script to validate Django 5.2.5 upgrade functionality
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

def test_django_version():
    """Test Django version"""
    print(f"Django version: {django.get_version()}")
    version_tuple = django.VERSION
    if version_tuple[0] == 5 and version_tuple[1] == 2:
        print("✅ Django 5.2.x is installed correctly!")
        return True
    else:
        print(f"❌ Expected Django 5.2.x, got {version_tuple}")
        return False

def test_models():
    """Test model imports and basic functionality"""
    try:
        from events.models import Event, EventType, Department
        from accounts.models import UserProfile
        from notifications.models import Notification
        from reports.models import Report
        
        print("✅ All models imported successfully!")
        
        # Test basic model functionality
        event_count = Event.objects.count()
        print(f"✅ Event model accessible: {event_count} events in database")
        
        user_count = UserProfile.objects.count()
        print(f"✅ UserProfile model accessible: {user_count} profiles in database")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_admin():
    """Test Django admin functionality"""
    try:
        from django.contrib import admin
        from django.urls import reverse
        
        admin_url = reverse('admin:index')
        print(f"✅ Django admin accessible at: {admin_url}")
        return True
    except Exception as e:
        print(f"❌ Admin test failed: {e}")
        return False

def test_urls():
    """Test URL configuration"""
    try:
        from django.urls import reverse
        
        urls_to_test = [
            ('events:home', 'Home page'),
            ('accounts:login', 'Login page'),
            ('admin:index', 'Admin page'),
        ]
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description} URL error: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ URL test failed: {e}")
        return False

def test_forms():
    """Test forms functionality"""
    try:
        from events.forms import EventForm
        from accounts.forms import UserRegistrationForm
        
        print("✅ Forms imported successfully!")
        
        # Test basic form instantiation
        event_form = EventForm()
        user_form = UserRegistrationForm()
        
        print("✅ Forms can be instantiated!")
        return True
    except Exception as e:
        print(f"❌ Forms test failed: {e}")
        return False

def test_templates():
    """Test template configuration"""
    try:
        from django.template.loader import get_template
        
        templates_to_test = [
            'base.html',
            'events/home.html',
            'accounts/login.html',
        ]
        
        for template_name in templates_to_test:
            try:
                template = get_template(template_name)
                print(f"✅ Template found: {template_name}")
            except Exception as e:
                print(f"⚠️  Template {template_name}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def test_migrations():
    """Test migration status"""
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  {len(plan)} unapplied migrations found")
            for migration, backwards in plan:
                print(f"  - {migration}")
            return False
        else:
            print("✅ All migrations are applied!")
            return True
            
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False

def main():
    print("=== DJANGO 5.2.5 FUNCTIONALITY TEST ===\n")
    
    try:
        django.setup()
        
        tests = [
            ("Django Version", test_django_version),
            ("Models", test_models),
            ("Admin", test_admin),
            ("URLs", test_urls),
            ("Forms", test_forms),
            ("Templates", test_templates),
            ("Migrations", test_migrations),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed!")
        
        print(f"\n=== RESULTS ===")
        print(f"Passed: {passed}/{total} tests")
        
        if passed == total:
            print("🎉 All tests passed! Django 5.2.5 upgrade is successful!")
            print("\nNext steps:")
            print("1. Run: python manage.py runserver")
            print("2. Test the application in your browser")
            print("3. Verify all features work as expected")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Please review and fix issues.")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)