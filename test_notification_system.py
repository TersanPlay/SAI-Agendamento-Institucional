#!/usr/bin/env python
"""
Test script to validate the notification system functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

from notifications.models import Notification, NotificationPreference
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.test import Client

def test_notification_system():
    print("=== TESTING NOTIFICATION SYSTEM ===\n")
    
    # Test 1: Template Loading
    try:
        template = get_template('notifications/notification_list.html')
        print("✅ Template loads successfully")
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        return False
    
    # Test 2: Model Functionality
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in system")
            return False
        
        # Create test notification
        notification = Notification.objects.create(
            recipient=user,
            title='System Test Notification',
            message='Testing notification system functionality',
            notification_type='system_alert',
            priority='medium'
        )
        print(f"✅ Created test notification (ID: {notification.id})")
        
        # Test notification methods
        notification.mark_as_read()
        print("✅ Mark as read functionality works")
        
        # Clean up
        notification.delete()
        print("✅ Notification deletion works")
        
    except Exception as e:
        print(f"❌ Model functionality failed: {e}")
        return False
    
    # Test 3: URL Resolution
    try:
        from django.urls import reverse
        url = reverse('notifications:list')
        print(f"✅ Notification list URL resolves: {url}")
        
        pref_url = reverse('notifications:preferences')
        print(f"✅ Notification preferences URL resolves: {pref_url}")
        
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return False
    
    # Test 4: View Response (without authentication for basic check)
    try:
        client = Client()
        # This will redirect to login, but shouldn't cause template errors
        response = client.get('/notifications/')
        print(f"✅ Notification view responds (Status: {response.status_code})")
        
    except Exception as e:
        print(f"❌ View response failed: {e}")
        return False
    
    # Test 5: Notification Types
    try:
        types = dict(Notification.NOTIFICATION_TYPES)
        print(f"✅ Available notification types: {len(types)}")
        for key, value in types.items():
            print(f"   - {key}: {value}")
        
    except Exception as e:
        print(f"❌ Notification types test failed: {e}")
        return False
    
    print("\n🎉 All notification system tests passed!")
    return True

if __name__ == "__main__":
    success = test_notification_system()
    sys.exit(0 if success else 1)