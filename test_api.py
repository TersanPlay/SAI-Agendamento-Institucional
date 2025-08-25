import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('c:\\Users\\Play\\pop')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

# Import the dashboard view function
from events.dashboard_views import dashboard_metrics_api
from django.http import HttpRequest
from django.contrib.auth.models import User

# Create a mock request
request = HttpRequest()
request.method = 'GET'
request.GET = {
    'start_date': '2025-07-25',
    'end_date': '2025-08-24'
}

# Create a mock user
user = User.objects.first()
request.user = user

print("Testing dashboard API...")
print("User:", user)
print("User profile:", getattr(user, 'profile', 'No profile'))

# Call the function
try:
    response = dashboard_metrics_api(request)
    print("Status code:", response.status_code)
    print("Response content:", response.content.decode('utf-8')[:200])
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()