import os
import sys
import django
from django.urls import reverse

# Add the project directory to the Python path
sys.path.append('c:\\Users\\Play\\pop')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

# Test if the URL pattern exists
try:
    from django.urls import reverse
    url = reverse('events:dashboard_metrics_api')
    print(f"URL resolved successfully: {url}")
except Exception as e:
    print(f"URL resolution error: {e}")

# Test database access
try:
    from events.models import Event
    # Using getattr to avoid static analysis issues with Django model managers
    objects_manager = getattr(Event, 'objects', None)
    if objects_manager:
        count = objects_manager.count()
        print(f"Database access successful. Event count: {count}")
    else:
        print("Database access error: Event.objects manager not found")
except Exception as e:
    print(f"Database access error: {e}")

# Test user access
try:
    from django.contrib.auth.models import User
    user = User.objects.first()
    if user:
        print(f"User found: {user.username}")
        if hasattr(user, 'profile'):
            print(f"User profile exists. Is admin: {user.profile.is_administrator}")
        else:
            print("User profile does not exist")
    else:
        print("No users found in database")
except Exception as e:
    print(f"User access error: {e}")