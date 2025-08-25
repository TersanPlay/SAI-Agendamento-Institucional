#!/usr/bin/env python
"""
Test script to verify public calendar access restriction
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

def test_public_calendar_access_restriction():
    """Test that public calendar now requires authentication"""
    print("=== Testing Public Calendar Access Restriction ===\n")
    
    try:
        django.setup()
        
        from django.test import Client
        from django.urls import reverse
        from django.contrib.auth.models import User
        
        # Create test client
        client = Client()
        
        # Test 1: Unauthenticated access should redirect to login
        print("Test 1: Unauthenticated access to public calendar")
        response = client.get(reverse('events:public_calendar'))
        print(f"Status code: {response.status_code}")
        if response.status_code == 302:
            print("✅ PASS: Redirects to login (requires authentication)")
            redirect_url = response.url
            if 'login' in redirect_url:
                print(f"✅ Redirects to login page: {redirect_url}")
            else:
                print(f"⚠️  Redirects to: {redirect_url}")
        else:
            print("❌ FAIL: Should redirect to login but didn't")
            return False
        
        # Test 2: Test authenticated access
        print("\nTest 2: Authenticated access to public calendar")
        
        # Create test user
        test_user = User.objects.create_user(
            username='test_user_calendar',
            email='test@example.com',
            password='testpass123'
        )
        
        # Login the user
        login_success = client.login(username='test_user_calendar', password='testpass123')
        if login_success:
            print("✅ User logged in successfully")
            
            # Try accessing public calendar again
            response = client.get(reverse('events:public_calendar'))
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ PASS: Authenticated user can access public calendar")
            else:
                print(f"❌ FAIL: Authenticated user cannot access public calendar (status: {response.status_code})")
                return False
        else:
            print("❌ FAIL: Could not login test user")
            return False
        
        # Test 3: Test public calendar export access
        print("\nTest 3: Testing public calendar export access")
        
        # Logout first
        client.logout()
        
        # Try accessing export without authentication
        response = client.get(reverse('events:export_public_calendar_ics'))
        print(f"Export access (unauthenticated) status code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ PASS: Export also requires authentication")
        else:
            print("❌ FAIL: Export should require authentication")
            return False
        
        # Test authenticated export access
        client.login(username='test_user_calendar', password='testpass123')
        response = client.get(reverse('events:export_public_calendar_ics'))
        print(f"Export access (authenticated) status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Authenticated user can access export")
        else:
            print(f"⚠️  Export status: {response.status_code}")
        
        # Cleanup
        test_user.delete()
        
        print("\n🎉 All tests passed! Public calendar access is now restricted to logged-in users.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_public_calendar_access_restriction()
    sys.exit(0 if success else 1)