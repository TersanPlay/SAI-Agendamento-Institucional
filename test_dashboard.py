import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to the Python path
sys.path.append('c:\\Users\\Play\\pop')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventosys.settings')
django.setup()

# Import the dashboard view function
from events.dashboard_views import dashboard_metrics_api
from django.http import HttpRequest

# Create a mock request
request = HttpRequest()
request.method = 'GET'
request.GET = {
    'start_date': '2025-07-25',
    'end_date': '2025-08-24'
}

# Call the function
try:
    response = dashboard_metrics_api(request)
    print("Status code:", response.status_code)
    print("Response content:", response.content.decode('utf-8')[:200])
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()