from django.urls import path
from . import views
from . import utils
from . import dashboard_views
from . import feed_views

app_name = 'events'

urlpatterns = [
    # Home and dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('test-api/', views.test_api_view, name='test_api'),
    path('debug-dashboard-api/', views.debug_dashboard_api, name='debug_dashboard_api'),
    
    # Event CRUD
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<uuid:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<uuid:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/data/', views.calendar_data_view, name='calendar_data'),
    path('calendar/public/', views.public_calendar_view, name='public_calendar'),
    
    # Calendar exports
    path('calendar/export/ics/', utils.export_calendar_ics, name='export_calendar_ics'),
    path('calendar/export/pdf/', utils.export_calendar_pdf, name='export_calendar_pdf'),
    path('calendar/public/export/ics/', utils.export_public_calendar_ics, name='export_public_calendar_ics'),
    
    # Dashboard monitoring
    path('dashboard/monitoring/', dashboard_views.monitoring_dashboard, name='monitoring_dashboard'),
    path('dashboard/api/metrics/', dashboard_views.dashboard_metrics_api, name='dashboard_metrics_api'),
    path('dashboard/api/trends/', dashboard_views.event_trends_api, name='event_trends_api'),
    path('dashboard/api/performance/', dashboard_views.performance_metrics_api, name='performance_metrics_api'),
    
    # Calendar integrations
    path('calendar/integration/', feed_views.calendar_integration_info, name='calendar_integration'),
    path('calendar/feed/user/<int:user_id>/<str:token>/', feed_views.user_calendar_feed, name='user_calendar_feed'),
    path('calendar/feed/department/<int:department_id>/', feed_views.department_calendar_feed, name='department_calendar_feed'),
    path('calendar/feed/public/', feed_views.public_calendar_feed, name='public_calendar_feed'),
]