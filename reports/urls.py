from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Unified reports page
    path('', views.reports_view, name='list'),
    path('advanced/', views.reports_view, name='advanced'),
    path('export/', views.export_report, name='export'),
    path('api/data/', views.report_data_api, name='api_data'),
    path('api/locations/', views.locations_api, name='api_locations'),
    path('api/trend/', views.trend_data_api, name='api_trend'),
    path('debug/', views.debug_view, name='debug'),  # Debug endpoint
    # Removed old URLs: create/ and generate/<int:report_id>/
]