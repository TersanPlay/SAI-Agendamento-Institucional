from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from events.models import Department, EventType, Event
from accounts.models import UserProfile
from datetime import datetime, timedelta


class ReportsViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile
        self.profile = UserProfile.objects.create(
            user=self.user,
            user_type='administrador',
            is_administrator=True
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department for reports'
        )
        
        # Create test event type
        self.event_type = EventType.objects.create(
            name='reuniao',
            color='#3B82F6',
            icon='fas fa-calendar'
        )
        
        # Create test event
        self.event = Event.objects.create(
            name='Test Event',
            event_type=self.event_type,
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=2),
            location_mode='presencial',
            target_audience='publico_interno',
            responsible_person=self.user,
            department=self.department,
            status='planejado',
            created_by=self.user
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_reports_page_loads(self):
        """Test that the reports page loads successfully"""
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatórios Avançados')
    
    def test_api_data_endpoint(self):
        """Test that the API data endpoint returns JSON data"""
        response = self.client.get(reverse('reports:api_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('total_events', data)
        self.assertIn('completed_events', data)
        self.assertIn('events', data)
    
    def test_responsible_persons_api(self):
        """Test that the responsible persons API returns data"""
        response = self.client.get(reverse('reports:api_responsibles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('responsible_persons', data)
    
    def test_locations_api(self):
        """Test that the locations API returns data"""
        response = self.client.get(reverse('reports:api_locations'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('locations', data)
    
    def test_trend_data_api(self):
        """Test that the trend data API returns data"""
        response = self.client.get(reverse('reports:api_trend'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('months', data)
        self.assertIn('event_counts', data)
    
    def test_export_report(self):
        """Test that the export report endpoint works"""
        # Test PDF export
        response = self.client.post(reverse('reports:export'), {
            'report_type': 'events_by_period',
            'format': 'pdf',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Test Excel export
        response = self.client.post(reverse('reports:export'), {
            'report_type': 'events_by_period',
            'format': 'excel',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Test CSV export
        response = self.client.post(reverse('reports:export'), {
            'report_type': 'events_by_period',
            'format': 'csv',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')