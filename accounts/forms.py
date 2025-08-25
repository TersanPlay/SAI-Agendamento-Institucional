from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile  # Import the model directly
from events.models import Department  # Import Department directly to avoid circular import issues


class UserRegistrationForm(UserCreationForm):
    """Formulário para registro de novos usuários"""
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    user_type = forms.ChoiceField(
        choices=[],  # Will be set in __init__
        required=True,
        label='Tipo de Usuário',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Departamento',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = UserProfile.USER_TYPES
        self.fields['department'].queryset = Department.objects.all()
        
        # Adicionar classes CSS para Tailwind
        for field_name, field in self.fields.items():
            if field_name not in ['user_type', 'department']:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Criar ou atualizar o perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.user_type = self.cleaned_data['user_type']
            profile.department = self.cleaned_data['department']
            profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário"""
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    email = forms.EmailField(required=True, label='Email')
    
    class Meta:
        model = UserProfile  # Using direct model reference
        fields = [
            'phone', 'avatar', 'receive_notifications', 
            'calendar_view_preference', 'department'
        ]
        labels = {
            'phone': 'Telefone',
            'avatar': 'Foto do Perfil',
            'receive_notifications': 'Receber Notificações',
            'calendar_view_preference': 'Visualização Preferida do Calendário',
            'department': 'Departamento',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '(00) 00000-0000'
            }),
            'calendar_view_preference': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'receive_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),  # type: ignore
            'avatar': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Set department queryset
        self.fields['department'].queryset = Department.objects.all()
        
        # Adicionar classes CSS para campos de texto
        for field_name in ['first_name', 'last_name', 'email']:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Atualizar dados do usuário
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile


class UserTypeUpdateForm(forms.ModelForm):
    """Formulário para administradores atualizarem o tipo de usuário"""
    class Meta:
        model = UserProfile  # Using direct model reference
        fields = ['user_type', 'department']
        labels = {
            'user_type': 'Tipo de Usuário',
            'department': 'Departamento',
        }
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set department queryset
        self.fields['department'].queryset = Department.objects.all()