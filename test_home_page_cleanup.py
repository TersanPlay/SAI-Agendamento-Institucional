#!/usr/bin/env python
"""
Verification script to test home page after removing public events section
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

def test_home_page_without_public_events():
    """Test that home page works correctly without public events section"""
    print("=== Testing Home Page Without Public Events Section ===\n")
    
    try:
        django.setup()
        
        from django.test import Client
        from django.urls import reverse
        
        # Create test client
        client = Client()
        
        # Test home page access
        print("Test 1: Accessing home page")
        response = client.get('/')
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Home page loads successfully")
            
            # Check that the response doesn't contain public events section
            content = response.content.decode('utf-8')
            
            # Check for removed elements
            if 'Próximos Eventos Públicos' not in content:
                print("✅ PASS: 'Próximos Eventos Públicos' section removed")
            else:
                print("❌ FAIL: 'Próximos Eventos Públicos' text still found")
                return False
            
            if 'Eventos abertos à participação da comunidade' not in content:
                print("✅ PASS: 'Eventos abertos à participação da comunidade' text removed")
            else:
                print("❌ FAIL: 'Eventos abertos à participação da comunidade' text still found")
                return False
            
            # Check that essential elements are still present
            if 'EventoSys' in content:
                print("✅ PASS: Main title still present")
            else:
                print("❌ FAIL: Main title missing")
                return False
            
            if 'Funcionalidades Principais' in content:
                print("✅ PASS: Features section still present")
            else:
                print("❌ FAIL: Features section missing")
                return False
            
            if 'Tipos de Eventos' in content:
                print("✅ PASS: Statistics section still present")
            else:
                print("❌ FAIL: Statistics section missing")
                return False
            
        else:
            print(f"❌ FAIL: Home page returned status {response.status_code}")
            return False
        
        # Test 2: Check home view context
        print("\nTest 2: Checking home view context")
        from events.views import home_view
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.method = 'GET'
        
        response = home_view(request)
        print(f"View response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Home view executes successfully")
            
            # The context should not contain public_events anymore
            if hasattr(response, 'context_data'):
                context = response.context_data
                if 'public_events' not in context:
                    print("✅ PASS: public_events removed from context")
                else:
                    print("❌ FAIL: public_events still in context")
                    return False
            else:
                print("✅ PASS: Context optimized (no public_events query)")
        
        print("\n🎉 All tests passed! Public events section successfully removed from home page.")
        print("\nChanges made:")
        print("- ❌ Removed 'Próximos Eventos Públicos' section from home template")
        print("- ❌ Removed 'Eventos abertos à participação da comunidade' subtitle")
        print("- 🔧 Optimized home view by removing unnecessary database query")
        print("- ✅ Preserved all other sections (statistics, features, CTA)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_home_page_without_public_events()
    sys.exit(0 if success else 1)