from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification management
    path('', views.notification_list, name='list'),
    path('<int:pk>/', views.notification_detail, name='detail'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    
    # AJAX endpoints
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/recent/', views.get_recent_notifications, name='recent'),
    
    # Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
]