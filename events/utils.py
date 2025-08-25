from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from icalendar import Calendar, Event as ICalEvent
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import uuid
from datetime import datetime, timedelta
from accounts.utils import get_user_accessible_events
from .models import Event


@login_required
def export_calendar_ics(request):
    """Export calendar events to ICS format"""
    # Get user accessible events
    events = get_user_accessible_events(request.user)
    
    # Filter by date range if provided
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        events = events.filter(
            start_datetime__gte=start_date,
            end_datetime__lte=end_date
        )
    else:
        # Default to next 3 months
        now = timezone.now()
        three_months = now + timedelta(days=90)
        events = events.filter(
            start_datetime__gte=now,
            start_datetime__lte=three_months
        )
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//EventoSys//Sistema de Gestão de Eventos//PT')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'EventoSys - Eventos Institucionais')
    cal.add('x-wr-caldesc', 'Calendário de eventos institucionais')
    cal.add('x-wr-timezone', 'America/Sao_Paulo')
    
    # Add events
    for event in events.select_related('event_type', 'location', 'responsible_person'):
        ical_event = ICalEvent()
        ical_event.add('uid', f'event-{event.id}@eventosys.local')
        ical_event.add('dtstart', event.start_datetime)
        ical_event.add('dtend', event.end_datetime)
        ical_event.add('summary', event.name)
        ical_event.add('description', 
                      f'Tipo: {event.event_type.get_name_display()}\n'
                      f'Responsável: {event.responsible_person.get_full_name() or event.responsible_person.username}\n'
                      f'Status: {event.get_status_display()}\n\n'
                      f'{event.description}')
        
        if event.location:
            ical_event.add('location', str(event.location))
        
        if event.virtual_link:
            ical_event.add('url', event.virtual_link)
        
        ical_event.add('created', event.created_at)
        ical_event.add('last-modified', event.updated_at)
        ical_event.add('categories', event.event_type.get_name_display())
        ical_event.add('status', 'CONFIRMED' if event.status in ['planejado', 'em_andamento'] else 'CANCELLED')
        
        cal.add_component(ical_event)
    
    # Generate response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="eventosys_calendar_{timezone.now().strftime("%Y%m%d")}.ics"'
    return response


@login_required
def export_calendar_pdf(request):
    """Export calendar events to PDF format"""
    # Get user accessible events
    events = get_user_accessible_events(request.user)
    
    # Filter by date range if provided
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        events = events.filter(
            start_datetime__gte=start_date,
            end_datetime__lte=end_date
        )
        period_text = f"Período: {start_date} a {end_date}"
    else:
        # Default to current month
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_of_month.replace(month=start_of_month.month + 1 if start_of_month.month < 12 else 1,
                                          year=start_of_month.year if start_of_month.month < 12 else start_of_month.year + 1)
        events = events.filter(
            start_datetime__gte=start_of_month,
            start_datetime__lt=next_month
        )
        period_text = f"Período: {start_of_month.strftime('%B %Y')}"
    
    events = events.select_related('event_type', 'location', 'responsible_person', 'department').order_by('start_datetime')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=HexColor('#1f2937'),
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        textColor=HexColor('#6b7280'),
        alignment=1  # Center
    )
    
    elements.append(Paragraph("EventoSys - Calendário de Eventos", title_style))
    elements.append(Paragraph(period_text, subtitle_style))
    elements.append(Paragraph(f"Gerado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 20))
    
    if events.exists():
        # Create table data
        data = [['Data/Hora', 'Evento', 'Tipo', 'Local', 'Status', 'Responsável']]
        
        for event in events:
            data.append([
                event.start_datetime.strftime('%d/%m/%Y\n%H:%M'),
                Paragraph(event.name, styles['Normal']),
                event.event_type.get_name_display(),
                str(event.location) if event.location else '-',
                event.get_status_display(),
                event.responsible_person.get_full_name() or event.responsible_person.username
            ])
        
        # Create table
        table = Table(data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1*inch, 1.5*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f9fafb')])
        ]))
        
        elements.append(table)
        
        # Summary
        elements.append(Spacer(1, 30))
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6b7280')
        )
        
        total_events = events.count()
        status_counts = {}
        for event in events:
            status = event.get_status_display()
            status_counts[status] = status_counts.get(status, 0) + 1
        
        summary_text = f"<b>Resumo:</b> {total_events} evento(s) no período<br/>"
        for status, count in status_counts.items():
            summary_text += f"• {status}: {count}<br/>"
        
        elements.append(Paragraph(summary_text, summary_style))
        
    else:
        # No events message
        no_events_style = ParagraphStyle(
            'NoEvents',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#6b7280'),
            alignment=1
        )
        elements.append(Paragraph("Nenhum evento encontrado no período selecionado.", no_events_style))
    
    # Build PDF
    doc.build(elements)
    
    # Generate response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="eventosys_calendar_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response


@login_required
def export_public_calendar_ics(request):
    """Export public calendar events to ICS format (requires authentication)"""
    # Get only public events
    events = Event.objects.filter(is_public=True)
    
    # Filter by date range if provided
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        events = events.filter(
            start_datetime__gte=start_date,
            end_datetime__lte=end_date
        )
    else:
        # Default to next 3 months
        now = timezone.now()
        three_months = now + timedelta(days=90)
        events = events.filter(
            start_datetime__gte=now,
            start_datetime__lte=three_months
        )
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//EventoSys//Eventos Públicos//PT')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'EventoSys - Eventos Públicos')
    cal.add('x-wr-caldesc', 'Calendário de eventos públicos')
    cal.add('x-wr-timezone', 'America/Sao_Paulo')
    
    # Add events
    for event in events.select_related('event_type', 'location', 'responsible_person'):
        ical_event = ICalEvent()
        ical_event.add('uid', f'public-event-{event.id}@eventosys.local')
        ical_event.add('dtstart', event.start_datetime)
        ical_event.add('dtend', event.end_datetime)
        ical_event.add('summary', f'[PÚBLICO] {event.name}')
        ical_event.add('description', 
                      f'Evento público institucional\n\n'
                      f'Tipo: {event.event_type.get_name_display()}\n'
                      f'Responsável: {event.responsible_person.get_full_name() or event.responsible_person.username}\n\n'
                      f'{event.description}')
        
        if event.location:
            ical_event.add('location', str(event.location))
        
        if event.virtual_link:
            ical_event.add('url', event.virtual_link)
        
        ical_event.add('created', event.created_at)
        ical_event.add('last-modified', event.updated_at)
        ical_event.add('categories', f'Público,{event.event_type.get_name_display()}')
        ical_event.add('status', 'CONFIRMED' if event.status in ['planejado', 'em_andamento'] else 'CANCELLED')
        
        cal.add_component(ical_event)
    
    # Generate response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="eventosys_public_calendar_{timezone.now().strftime("%Y%m%d")}.ics"'
    return response