from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from accounts.utils import has_permission, can_edit_event, can_view_event, get_user_accessible_events, log_user_action
from .models import Event, EventType, Department, Location
from .forms import EventForm, EventFilterForm  # EventDocumentFormSet removed
import json


def home_view(request):
    """Página inicial pública"""
    context = {
        'event_types_count': EventType.objects.count(),  # type: ignore
        'departments_count': Department.objects.count(),  # type: ignore
    }
    return render(request, 'events/home.html', context)


@login_required
def dashboard_view(request):
    """Dashboard principal do sistema"""
    user = request.user
    
    # Eventos acessíveis ao usuário
    accessible_events = get_user_accessible_events(user)
    
    # Estatísticas
    today = timezone.now().date()
    events_today = accessible_events.filter(start_datetime__date=today)
    events_this_week = accessible_events.filter(
        start_datetime__date__gte=today,
        start_datetime__date__lt=today + timezone.timedelta(days=7)
    )
    my_events = accessible_events.filter(
        Q(created_by=user) | Q(responsible_person=user)
    )
    
    # Eventos por status
    events_by_status = accessible_events.values('status').annotate(
        count=Count('status')
    ).order_by('status')
    
    # Eventos por tipo
    events_by_type = accessible_events.values(
        'event_type__name'
    ).annotate(count=Count('event_type')).order_by('-count')[:5]
    
    # Eventos recentes
    recent_events = accessible_events.order_by('-created_at')[:5]
    
    context = {
        'events_today': events_today,
        'events_this_week': events_this_week,
        'my_events': my_events,
        'events_by_status': events_by_status,
        'events_by_type': events_by_type,
        'recent_events': recent_events,
        'can_create_events': has_permission(user, 'create_event'),
    }
    
    log_user_action(request, user, 'view_dashboard', 'dashboard')
    return render(request, 'events/dashboard.html', context)


def test_api_view(request):
    """Test view to check if API endpoint is working"""
    from events.dashboard_views import dashboard_metrics_api
    # Create a mock request object
    class MockRequest:
        def __init__(self):
            self.user = None
            self.GET = {'start_date': '2025-07-25', 'end_date': '2025-08-24'}
            self.method = 'GET'
    
    mock_request = MockRequest()
    # Try to call the dashboard metrics API
    try:
        response = dashboard_metrics_api(mock_request)
        return HttpResponse(f"API Test Result: {response.content[:200]}".encode('utf-8'))
    except Exception as e:
        return HttpResponse(f"API Test Error: {str(e)}".encode('utf-8'))


def debug_dashboard_api(request):
    """Debug view to check dashboard API access"""
    from django.contrib.auth.models import User
    from accounts.utils import has_permission
    
    # Get the first user
    user = User.objects.first()
    
    if not user:
        return HttpResponse("No users found".encode('utf-8'))
    
    # Check if user has profile
    if not hasattr(user, 'profile'):
        return HttpResponse("User has no profile".encode('utf-8'))
    
    # Check permissions
    has_perm = has_permission(user, 'view_reports')
    
    # Try to access the API directly
    from events.dashboard_views import dashboard_metrics_api
    
    # Create a request object with the user
    class MockRequest:
        def __init__(self, user):
            self.user = user
            self.GET = {'start_date': '2025-07-25', 'end_date': '2025-08-24'}
            self.method = 'GET'
    
    mock_request = MockRequest(user)
    
    try:
        response = dashboard_metrics_api(mock_request)
        return HttpResponse(f"User: {user.username}<br>"
                          f"Has profile: True<br>"
                          f"Is admin: {user.profile.is_administrator}<br>"
                          f"Has view_reports permission: {has_perm}<br>"
                          f"API Response status: {response.status_code}<br>"
                          f"API Response content: {response.content[:200]}".encode('utf-8'))
    except Exception as e:
        return HttpResponse(f"User: {user.username}<br>"
                          f"Has profile: True<br>"
                          f"Is admin: {user.profile.is_administrator}<br>"
                          f"Has view_reports permission: {has_perm}<br>"
                          f"API Error: {str(e)}".encode('utf-8'))


class EventListView(LoginRequiredMixin, ListView):
    """Lista de eventos com filtros"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = get_user_accessible_events(self.request.user)
        
        # Aplicar filtros
        form = EventFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('event_type'):
                queryset = queryset.filter(event_type=form.cleaned_data['event_type'])
            
            if form.cleaned_data.get('department'):
                queryset = queryset.filter(department=form.cleaned_data['department'])
            
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            if form.cleaned_data.get('responsible_person'):
                queryset = queryset.filter(responsible_person=form.cleaned_data['responsible_person'])
            
            if form.cleaned_data.get('start_date'):
                queryset = queryset.filter(start_datetime__date__gte=form.cleaned_data['start_date'])
            
            if form.cleaned_data.get('end_date'):
                queryset = queryset.filter(start_datetime__date__lte=form.cleaned_data['end_date'])
            
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(description__icontains=search_term)
                )
        
        return queryset.select_related('event_type', 'department', 'responsible_person', 'location')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EventFilterForm(self.request.GET)
        context['can_create_events'] = has_permission(self.request.user, 'create_event')
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    """Detalhe do evento"""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_view_event(self.request.user, obj):
            messages.error(self.request, 'Você não tem permissão para visualizar este evento.')
            return redirect('events:event_list')
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context['can_edit'] = can_edit_event(self.request.user, event)
        context['documents'] = []  # Documents functionality removed
        # Participants functionality removed as requested
        context['history'] = event.history.all()[:10]  # Últimas 10 alterações
        
        log_user_action(self.request, self.request.user, 'view_event', f'event_{event.id}')
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """Criação de evento"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not has_permission(request.user, 'create_event'):
            messages.error(request, 'Você não tem permissão para criar eventos.')
            return redirect('events:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):  # type: ignore
        event = form.save(commit=False)
        event.created_by = self.request.user
        event._current_user = self.request.user  # Para o signal
        
        from django.db import transaction
        with transaction.atomic():  # type: ignore
            event.save()
            
            # Document processing removed as requested
            # Participant processing removed as requested
        
        messages.success(self.request, f'Evento "{event.name}" criado com sucesso!')
        log_user_action(self.request, self.request.user, 'create_event', f'event_{event.id}')
        
        return redirect('events:event_detail', pk=event.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Document and participant formsets removed as requested
        return context


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """Edição de evento"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_edit_event(self.request.user, obj):
            messages.error(self.request, 'Você não tem permissão para editar este evento.')
            return redirect('events:event_detail', pk=obj.pk)
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):  # type: ignore
        event = form.save(commit=False)
        event._current_user = self.request.user  # Para o signal
        
        from django.db import transaction
        with transaction.atomic():  # type: ignore
            event.save()
            
            # Document processing removed as requested
            # Participant processing removed as requested
        
        messages.success(self.request, f'Evento "{event.name}" atualizado com sucesso!')
        log_user_action(self.request, self.request.user, 'update_event', f'event_{event.id}')
        
        return redirect('events:event_detail', pk=event.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Document and participant formsets removed as requested
        context['is_edit'] = True
        return context


class EventDeleteView(LoginRequiredMixin, DeleteView):
    """Exclusão de evento"""
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_edit_event(self.request.user, obj):
            messages.error(self.request, 'Você não tem permissão para excluir este evento.')
            # Return the redirect response instead of redirecting directly
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(reverse('events:event_detail', kwargs={'pk': obj.pk}))
        return obj
    
    def delete(self, request, *args, **kwargs):  # type: ignore
        event = self.get_object()
        # Check if event is an HttpResponseRedirect
        from django.http import HttpResponseRedirect
        if isinstance(event, HttpResponseRedirect):
            return event
            
        event_name = event.name
        response = super().delete(request, *args, **kwargs)
        
        messages.success(request, f'Evento "{event_name}" excluído com sucesso!')
        log_user_action(request, request.user, 'delete_event', f'event_{event.id}')
        
        return response


def calendar_data_view(request):
    """API para dados do calendário (JSON)"""
    # Check if it's a public request
    public_only = request.GET.get('public_only', 'false').lower() == 'true'
    
    if public_only:
        # Public events only
        events = Event.objects.filter(is_public=True)  # type: ignore
    else:
        # Check authentication for private access
        if not request.user.is_authenticated:
            events = Event.objects.filter(is_public=True)  # type: ignore
        else:
            events = get_user_accessible_events(request.user)
    
    # Date range filters
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        events = events.filter(
            start_datetime__gte=start_date,
            end_datetime__lte=end_date
        )
    
    # Advanced filters
    event_type = request.GET.get('event_type')
    if event_type:
        events = events.filter(event_type__name=event_type)
    
    department = request.GET.get('department')
    if department:
        events = events.filter(department_id=department)
    
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)
    
    # Select related to optimize queries
    events = events.select_related('event_type', 'location', 'responsible_person', 'department')
    
    # Convert to FullCalendar format
    calendar_events = []
    for event in events:
        # Determine text color based on background
        text_color = '#ffffff' if event.event_type.color else '#000000'
        
        calendar_events.append({
            'id': str(event.id),
            'title': event.name,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            # Remove the URL to prevent automatic navigation - we'll handle clicks in JavaScript
            'backgroundColor': event.event_type.color,
            'borderColor': event.event_type.color,
            'textColor': text_color,
            'extendedProps': {
                'type': event.event_type.get_name_display(),
                'status': event.get_status_display(),
                'location': str(event.location) if event.location else '',
                'responsible': event.responsible_person.get_full_name() or event.responsible_person.username,
                'department': event.department.name if event.department else '',
                'isPublic': event.is_public,
                'description': event.description[:100] + '...' if len(event.description) > 100 else event.description,
                # Add the URL to extendedProps so we can use it in the modal
                'url': reverse('events:event_detail', kwargs={'pk': event.pk}) if not public_only else '#',
            }
        })
    
    return JsonResponse(calendar_events, safe=False)


@login_required
def events_api(request):
    """API endpoint for dynamic event filtering"""
    # Get filter parameters from request
    queryset = get_user_accessible_events(request.user)
    
    # Apply filters using the same logic as EventListView
    form = EventFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('event_type'):
            queryset = queryset.filter(event_type=form.cleaned_data['event_type'])
        
        if form.cleaned_data.get('department'):
            queryset = queryset.filter(department=form.cleaned_data['department'])
        
        if form.cleaned_data.get('status'):
            queryset = queryset.filter(status=form.cleaned_data['status'])
        
        if form.cleaned_data.get('responsible_person'):
            queryset = queryset.filter(responsible_person=form.cleaned_data['responsible_person'])
        
        if form.cleaned_data.get('start_date'):
            queryset = queryset.filter(start_datetime__date__gte=form.cleaned_data['start_date'])
        
        if form.cleaned_data.get('end_date'):
            queryset = queryset.filter(start_datetime__date__lte=form.cleaned_data['end_date'])
        
        if form.cleaned_data.get('search'):
            search_term = form.cleaned_data['search']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
    
    # Apply the same select_related optimization
    queryset = queryset.select_related('event_type', 'department', 'responsible_person', 'location')
    
    # Pagination
    paginator = Paginator(queryset, 20)  # Same as EventListView
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the events grid HTML
    events_html = render_to_string('events/partials/events_grid.html', {
        'events': page_obj,
        'page_obj': page_obj,
        'request': request
    })
    
    # Return JSON response
    return JsonResponse({
        'events_html': events_html,
        'total_count': paginator.count,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'start_index': page_obj.start_index() if page_obj else 0,
        'end_index': page_obj.end_index() if page_obj else 0,
    })


@login_required
def public_calendar_view(request):
    """Calendário público (apenas eventos públicos) - Acesso restrito a usuários logados"""
    return render(request, 'events/public_calendar.html')


@login_required
def calendar_view(request):
    """Página do calendário interativo"""
    context = {
        'can_create_events': has_permission(request.user, 'create_event'),
        'event_types': EventType.objects.all(),  # type: ignore
        'departments': Department.objects.all(),  # type: ignore
    }
    return render(request, 'events/calendar.html', context)