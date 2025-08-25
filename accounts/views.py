from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, AccessLog
from .utils import log_user_action


def user_login(request):
    """View para login do usuário"""
    if request.user.is_authenticated:
        return redirect('events:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                log_user_action(request, user, 'login', 'user_session')
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                next_page = request.GET.get('next', 'events:dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Credenciais inválidas.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """View para logout do usuário"""
    if request.user.is_authenticated:
        log_user_action(request, request.user, 'logout', 'user_session')
        logout(request)
        messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('events:home')


class UserRegistrationView(CreateView):
    """View para registro de novos usuários (apenas para administradores)"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Usuário criado com sucesso!')
        # Log the action with the newly created user's ID
        log_user_action(self.request, self.request.user, 'create_user', f'user_{user.id}')
        return super().form_valid(form)


@login_required
def profile_view(request):
    """View para visualizar o perfil do usuário"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)  # type: ignore
    return render(request, 'accounts/profile.html', {'profile': profile})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View para atualizar o perfil do usuário"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)  # type: ignore
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        log_user_action(self.request, self.request.user, 'update_profile', 'user_profile')
        return response


@login_required
def access_logs_view(request):
    """View para visualizar logs de acesso (apenas administradores)"""
    if not request.user.profile.is_administrator:
        messages.error(request, 'Acesso negado.')
        return redirect('events:dashboard')
    
    # Get all logs ordered by timestamp (newest first)
    logs_list = AccessLog.objects.all().order_by('-timestamp')  # type: ignore
    
    # Create paginator with 20 items per page
    paginator = Paginator(logs_list, 20)
    
    # Get page number from request
    page_number = request.GET.get('page')
    
    # Get the page object
    page_obj = paginator.get_page(page_number)
    
    # Calculate counts for the summary statistics (using all logs, not just current page)
    today = timezone.now().date()
    logs_today_count = logs_list.filter(timestamp__date=today).count()
    successful_logins_count = logs_list.filter(action='login', success=True).count()
    failed_attempts_count = logs_list.filter(success=False).count()
    
    context = {
        'logs': page_obj,  # This will be the paginated logs
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'logs_today_count': logs_today_count,
        'successful_logins_count': successful_logins_count,
        'failed_attempts_count': failed_attempts_count,
    }
    
    return render(request, 'accounts/access_logs.html', context)


@login_required
def user_management_view(request):
    """View para gerenciamento de usuários (apenas administradores)"""
    if not request.user.profile.is_administrator:
        messages.error(request, 'Acesso negado.')
        return redirect('events:dashboard')
    
    users = User.objects.select_related('profile').all()
    return render(request, 'accounts/user_management.html', {'users': users})