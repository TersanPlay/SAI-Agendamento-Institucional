"""
Calendar feed views for external calendar subscriptions
"""
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.contrib.sites.models import Site
from datetime import timedelta
import hashlib

# Direct import of Event class
from events.models import Event, Department
from events.integrations import CalendarFeedIntegration, GoogleCalendarIntegration, OutlookIntegration
from accounts.utils import get_user_accessible_events


@require_GET
@cache_page(60 * 30)  # Cache for 30 minutes
def user_calendar_feed(request, user_id, token):
    """
    Personal calendar feed for a specific user
    Requires authentication token for security
    
    URL: /events/calendar/feed/user/<user_id>/<token>/
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Verify token
        expected_token = generate_user_token(user)
        if token != expected_token:
            raise Http404("Invalid token")
        
        # Generate calendar feed
        calendar = CalendarFeedIntegration.generate_user_calendar_feed(user, include_private=True)
        
        # Return iCalendar response
        response = HttpResponse(calendar.to_ical(), content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="eventosys_user_{user.username}.ics"'
        response['Cache-Control'] = 'max-age=1800'  # 30 minutes
        
        return response
        
    except Exception as e:
        raise Http404("Calendar feed not found")


@require_GET
@cache_page(60 * 60)  # Cache for 1 hour
def department_calendar_feed(request, department_id):
    """
    Public calendar feed for a specific department
    
    URL: /events/calendar/feed/department/<department_id>/
    """
    try:
        department = get_object_or_404(Department, id=department_id)
        
        # Generate calendar feed
        calendar = CalendarFeedIntegration.generate_department_calendar_feed(department)
        
        # Return iCalendar response
        response = HttpResponse(calendar.to_ical(), content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="eventosys_dept_{department.name.lower()}.ics"'
        response['Cache-Control'] = 'max-age=3600'  # 1 hour
        
        return response
        
    except Exception as e:
        raise Http404("Department calendar feed not found")


@require_GET
@cache_page(60 * 60)  # Cache for 1 hour
def public_calendar_feed(request):
    """
    Public calendar feed for all public events
    
    URL: /events/calendar/feed/public/
    """
    try:
        # Get public events
        events = Event.objects.filter(is_public=True)  # type: ignore
        
        # Filter future events (next 6 months)
        now = timezone.now()
        six_months = now + timedelta(days=180)
        events = events.filter(
            start_datetime__gte=now,
            start_datetime__lte=six_months
        ).select_related('event_type', 'location', 'responsible_person', 'department')
        
        # Create calendar
        from icalendar import Calendar
        cal = Calendar()
        cal.add('prodid', '-//EventoSys//Eventos Públicos//PT')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', 'EventoSys - Eventos Públicos')
        cal.add('x-wr-caldesc', 'Calendário público de eventos institucionais')
        cal.add('x-wr-timezone', 'America/Sao_Paulo')
        
        # Add events
        for event in events:
            ical_event = CalendarFeedIntegration._create_ical_event(event)
            cal.add_component(ical_event)
        
        # Return iCalendar response
        response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="eventosys_public.ics"'
        response['Cache-Control'] = 'max-age=3600'  # 1 hour
        
        return response
        
    except Exception as e:
        raise Http404("Public calendar feed not found")


@login_required
def calendar_integration_info(request):
    """
    Provide calendar integration information and URLs for the user
    
    URL: /events/calendar/integration/
    """
    user = request.user
    
    # Generate user token
    user_token = generate_user_token(user)
    
    # Get site domain
    try:
        site = Site.objects.get_current()
        domain = site.domain
        if not domain.startswith('http'):
            domain = f"https://{domain}"
    except:
        domain = request.build_absolute_uri('/').rstrip('/')
    
    # Build URLs
    user_feed_url = f"{domain}/events/calendar/feed/user/{user.id}/{user_token}/"
    public_feed_url = f"{domain}/events/calendar/feed/public/"
    
    # Department feed URL if user has department
    department_feed_url = None
    if hasattr(user, 'profile') and user.profile.department:
        department_feed_url = f"{domain}/events/calendar/feed/department/{user.profile.department.id}/"
    
    # Get sample event for integration links
    sample_event = get_user_accessible_events(user).filter(
        start_datetime__gte=timezone.now()
    ).first()
    
    google_url = None
    outlook_url = None
    if sample_event:
        google_url = GoogleCalendarIntegration.get_google_calendar_url(sample_event)
        outlook_url = OutlookIntegration.get_outlook_calendar_url(sample_event)
    
    context = {
        'user_feed_url': user_feed_url,
        'public_feed_url': public_feed_url,
        'department_feed_url': department_feed_url,
        'sample_google_url': google_url,
        'sample_outlook_url': outlook_url,
        'user_token': user_token,
        'has_sample_event': sample_event is not None,
        'sample_event': sample_event,
    }
    
    return render(request, 'events/calendar_integration.html', context)


def generate_user_token(user):
    """
    Generate secure token for user calendar feed
    
    Args:
        user: User object
        
    Returns:
        str: SHA256 token
    """
    from django.conf import settings
    
    # Create token from user ID, username, and secret key
    token_string = f"{user.id}-{user.username}-{settings.SECRET_KEY}"
    return hashlib.sha256(token_string.encode()).hexdigest()[:16]