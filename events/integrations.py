from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.contrib.sites.models import Site
from icalendar import Calendar, Event as ICalEvent, Alarm
from datetime import timedelta
from urllib.parse import urlencode
from .models import Event
import logging

logger = logging.getLogger('events')


class GoogleCalendarIntegration:
    """
    Google Calendar integration utilities
    """
    
    @staticmethod
    def get_google_calendar_url(event):
        """
        Generate Google Calendar add event URL
        
        Args:
            event: Event object
            
        Returns:
            str: Google Calendar URL
        """
        base_url = "https://calendar.google.com/calendar/render"
        
        # Format dates for Google Calendar (YYYYMMDDTHHMMSSZ format)
        start_time = event.start_datetime.strftime('%Y%m%dT%H%M%SZ')
        end_time = event.end_datetime.strftime('%Y%m%dT%H%M%SZ')
        
        # Build parameters
        params = {
            'action': 'TEMPLATE',
            'text': event.name,
            'dates': f"{start_time}/{end_time}",
            'details': GoogleCalendarIntegration._format_event_description(event),
            'location': str(event.location) if event.location else '',
            'trp': 'false'  # Don't show in guest list
        }
        
        # Convert to URL query string
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"
    
    @staticmethod
    def _format_event_description(event):
        """Format event description for Google Calendar"""
        description_parts = []
        
        # Basic info
        description_parts.append(f"Tipo: {event.event_type.get_name_display()}")
        
        if event.department:
            description_parts.append(f"Departamento: {event.department.name}")
        
        description_parts.append(f"Responsável: {event.responsible_person.get_full_name() or event.responsible_person.username}")
        
        if event.location_mode != 'presencial':
            description_parts.append(f"Modalidade: {event.get_location_mode_display()}")
        
        if event.virtual_link:
            description_parts.append(f"Link: {event.virtual_link}")
        
        # Event description
        if event.description:
            description_parts.append("")
            description_parts.append(event.description)
        
        # System info
        description_parts.append("")
        description_parts.append("---")
        description_parts.append("Evento criado via EventoSys")
        
        return "\\n".join(description_parts)


class OutlookIntegration:
    """
    Microsoft Outlook integration utilities
    """
    
    @staticmethod
    def get_outlook_calendar_url(event):
        """
        Generate Outlook Calendar add event URL
        
        Args:
            event: Event object
            
        Returns:
            str: Outlook Calendar URL
        """
        base_url = "https://outlook.live.com/calendar/0/deeplink/compose"
        
        # Format dates for Outlook (ISO format)
        start_time = event.start_datetime.isoformat()
        end_time = event.end_datetime.isoformat()
        
        # Build parameters
        params = {
            'subject': event.name,
            'startdt': start_time,
            'enddt': end_time,
            'body': OutlookIntegration._format_event_description(event),
            'location': str(event.location) if event.location else '',
            'path': '/calendar/action/compose'
        }
        
        # Convert to URL query string
        query_params = []
        for key, value in params.items():
            if value:  # Only add non-empty values
                query_params.append(f"{key}={value}")
        
        return f"{base_url}?{'&'.join(query_params)}"
    
    @staticmethod
    def _format_event_description(event):
        """Format event description for Outlook"""
        description_parts = []
        
        # Basic info
        description_parts.append(f"Tipo: {event.event_type.get_name_display()}")
        
        if event.department:
            description_parts.append(f"Departamento: {event.department.name}")
        
        description_parts.append(f"Responsável: {event.responsible_person.get_full_name() or event.responsible_person.username}")
        
        if event.location_mode != 'presencial':
            description_parts.append(f"Modalidade: {event.get_location_mode_display()}")
        
        if event.virtual_link:
            description_parts.append(f"Link: {event.virtual_link}")
        
        # Event description
        if event.description:
            description_parts.append("")
            description_parts.append(event.description)
        
        # System info
        description_parts.append("")
        description_parts.append("---")
        description_parts.append("Evento criado via EventoSys")
        
        return "%0D%0A".join(description_parts)  # URL-encoded line breaks


class CalendarFeedIntegration:
    """
    Calendar feed integration for external calendar subscriptions
    """
    
    @staticmethod
    def generate_user_calendar_feed(user, include_private=True):
        """
        Generate personalized calendar feed for a user
        
        Args:
            user: User object
            include_private: Include private events the user has access to
            
        Returns:
            Calendar: iCalendar object
        """
        from accounts.utils import get_user_accessible_events
        from django.apps import apps
        
        # Get user accessible events
        if include_private:
            events = get_user_accessible_events(user)
        else:
            EventModel = apps.get_model('events', 'Event')
            events = EventModel.objects.filter(is_public=True)
        
        # Filter future events (next 6 months)
        now = timezone.now()
        six_months = now + timedelta(days=180)
        events = events.filter(
            start_datetime__gte=now,
            start_datetime__lte=six_months
        ).select_related('event_type', 'location', 'responsible_person', 'department')
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', f'-//EventoSys//Calendário de {user.get_full_name() or user.username}//PT')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'EventoSys - {user.get_full_name() or user.username}')
        cal.add('x-wr-caldesc', f'Calendário personalizado de eventos para {user.get_full_name() or user.username}')
        cal.add('x-wr-timezone', 'America/Sao_Paulo')
        cal.add('x-wr-relcalid', f'eventosys-user-{user.id}')
        
        # Add events
        for event in events:
            ical_event = CalendarFeedIntegration._create_ical_event(event, user)
            cal.add_component(ical_event)
        
        return cal
    
    @staticmethod
    def generate_department_calendar_feed(department):
        """
        Generate calendar feed for a specific department
        
        Args:
            department: Department object
            
        Returns:
            Calendar: iCalendar object
        """
        from django.apps import apps
        
        # Get department events
        EventModel = apps.get_model('events', 'Event')
        events = EventModel.objects.filter(
            department=department,
            is_public=True
        )
        
        # Filter future events (next 6 months)
        now = timezone.now()
        six_months = now + timedelta(days=180)
        events = events.filter(
            start_datetime__gte=now,
            start_datetime__lte=six_months
        ).select_related('event_type', 'location', 'responsible_person')
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', f'-//EventoSys//Calendário {department.name}//PT')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'EventoSys - {department.name}')
        cal.add('x-wr-caldesc', f'Calendário de eventos do {department.name}')
        cal.add('x-wr-timezone', 'America/Sao_Paulo')
        cal.add('x-wr-relcalid', f'eventosys-dept-{department.id}')
        
        # Add events
        for event in events:
            ical_event = CalendarFeedIntegration._create_ical_event(event)
            cal.add_component(ical_event)
        
        return cal
    
    @staticmethod
    def _create_ical_event(event, user=None):
        """Create iCalendar event with proper formatting and alarms"""
        ical_event = ICalEvent()
        
        # Basic event info
        uid_prefix = f'user-{user.id}-' if user else 'public-'
        ical_event.add('uid', f'{uid_prefix}event-{event.id}@eventosys.local')
        ical_event.add('dtstart', event.start_datetime)
        ical_event.add('dtend', event.end_datetime)
        ical_event.add('dtstamp', timezone.now())
        
        # Event title with privacy indicator
        if user and not event.is_public:
            title = f"[PRIVADO] {event.name}"
        else:
            title = event.name
        ical_event.add('summary', title)
        
        # Detailed description
        description_parts = []
        description_parts.append(f"Tipo: {event.event_type.get_name_display()}")
        
        if event.department:
            description_parts.append(f"Departamento: {event.department.name}")
        
        description_parts.append(f"Responsável: {event.responsible_person.get_full_name() or event.responsible_person.username}")
        
        if event.location_mode != 'presencial':
            description_parts.append(f"Modalidade: {event.get_location_mode_display()}")
        
        if event.virtual_link:
            description_parts.append(f"Link: {event.virtual_link}")
        
        if event.expected_participants:
            description_parts.append(f"Participantes esperados: {event.expected_participants}")
        
        # Event description
        if event.description:
            description_parts.append("")
            description_parts.append("Descrição:")
            description_parts.append(event.description)
        
        # System signature
        description_parts.append("")
        description_parts.append("---")
        description_parts.append("Evento criado via EventoSys - Sistema de Gestão de Eventos Institucionais")
        
        if user:
            # Add personalized link to event details
            try:
                site = Site.objects.get_current()
                event_url = f"https://{site.domain}{reverse('events:event_detail', args=[event.id])}"
                description_parts.append(f"Ver detalhes: {event_url}")
            except:
                pass
        
        ical_event.add('description', '\\n'.join(description_parts))
        
        # Location
        if event.location:
            ical_event.add('location', str(event.location))
        
        # URL
        if event.virtual_link:
            ical_event.add('url', event.virtual_link)
        
        # Categories and classification
        categories = [event.event_type.get_name_display()]
        if event.department:
            categories.append(event.department.name)
        if not event.is_public:
            categories.append('Privado')
        
        ical_event.add('categories', ','.join(categories))
        
        # Event status
        if event.status == 'cancelado':
            ical_event.add('status', 'CANCELLED')
        elif event.status == 'concluido':
            ical_event.add('status', 'CONFIRMED')
        else:
            ical_event.add('status', 'CONFIRMED')
        
        # Priority based on event type
        priority_map = {
            'reuniao': 5,
            'audiencia_publica': 9,
            'sessao_plenaria': 9,
            'cerimonia_oficial': 8,
            'assembleia': 8,
            'coletiva_imprensa': 7,
        }
        priority = priority_map.get(event.event_type.name, 5)
        ical_event.add('priority', priority)
        
        # Transparency (show as busy or free)
        ical_event.add('transp', 'OPAQUE')  # Show as busy
        
        # Created and modified timestamps
        ical_event.add('created', event.created_at)
        ical_event.add('last-modified', event.updated_at)
        
        # Add alarms for upcoming events
        if event.start_datetime > timezone.now():
            # Add 24-hour reminder
            alarm_24h = Alarm()
            alarm_24h.add('action', 'DISPLAY')
            alarm_24h.add('description', f'Lembrete: {event.name} amanhã')
            alarm_24h.add('trigger', timedelta(hours=-24))
            ical_event.add_component(alarm_24h)
            
            # Add 1-hour reminder
            alarm_1h = Alarm()
            alarm_1h.add('action', 'DISPLAY')
            alarm_1h.add('description', f'Lembrete: {event.name} em 1 hora')
            alarm_1h.add('trigger', timedelta(hours=-1))
            ical_event.add_component(alarm_1h)
        
        return ical_event


class EmailInviteIntegration:
    """Email calendar invitation integration"""
    
    @staticmethod
    def send_calendar_invite(event, recipients, message=None):
        """
        Send calendar invitation via email
        
        Args:
            event: Event object
            recipients: List of email addresses
            message: Optional personal message
            
        Returns:
            bool: Success status
        """
        try:
            # Create iCalendar invitation
            cal = Calendar()
            cal.add('prodid', '-//EventoSys//Convite de Evento//PT')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'REQUEST')
            
            # Create event
            ical_event = CalendarFeedIntegration._create_ical_event(event)
            ical_event.add('organizer', f'MAILTO:{event.responsible_person.email}')
            
            # Add attendees
            for email in recipients:
                ical_event.add('attendee', f'MAILTO:{email};RSVP=TRUE')
            
            cal.add_component(ical_event)
            
            # Email content
            subject = f'Convite: {event.name}'
            
            # Render email template
            context = {
                'event': event,
                'message': message,
                'google_url': GoogleCalendarIntegration.get_google_calendar_url(event),
                'outlook_url': OutlookIntegration.get_outlook_calendar_url(event),
            }
            
            html_content = render_to_string('events/email/calendar_invite.html', context)
            text_content = render_to_string('events/email/calendar_invite.txt', context)
            
            # Send email with calendar attachment
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients
            )
            
            email.attach_alternative(html_content, "text/html")
            email.attach(
                f'evento_{event.id}.ics',
                cal.to_ical(),
                'text/calendar'
            )
            
            email.send()
            
            logger.info(f'Calendar invite sent for event {event.id} to {len(recipients)} recipients')
            return True
            
        except Exception as e:
            logger.error(f'Failed to send calendar invite for event {event.id}: {str(e)}')
            return False


class CalendarSyncIntegration:
    """Two-way calendar sync integration (future implementation)"""
    
    @staticmethod
    def sync_with_google_calendar(user, google_calendar_id):
        """Placeholder for Google Calendar sync"""
        # This would require Google Calendar API setup
        # Implementation would involve:
        # 1. OAuth authentication
        # 2. Reading events from Google Calendar
        # 3. Creating/updating events in EventoSys
        # 4. Pushing EventoSys events to Google Calendar
        logger.info(f'Google Calendar sync requested for user {user.username}')
        return False
    
    @staticmethod
    def sync_with_outlook_calendar(user, outlook_calendar_id):
        """Placeholder for Outlook Calendar sync"""
        # This would require Microsoft Graph API setup
        logger.info(f'Outlook Calendar sync requested for user {user.username}')
        return False