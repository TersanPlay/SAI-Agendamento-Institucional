from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile  # Import the model directly
from events.models import Department  # Import Department directly to avoid circular import issues


class UserRegistrationForm(UserCreationForm):
    """Formulário para registro de novos usuários - automaticamente configura como visualizador"""
    email = forms.EmailField(
        required=True, 
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu.email@exemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Nome',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu primeiro nome'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu sobrenome'
        })
    )
    department = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Departamento',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Selecione seu departamento (opcional)'
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Digite um nome de usuário único'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Digite uma senha segura'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirme sua senha'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        
        # Set required fields
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        
        # Adicionar classes CSS para Tailwind
        for field_name, field in self.fields.items():
            if field_name not in ['department']:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200'
                })
        
        # Aplicar classes CSS específicas para o campo department
        self.fields['department'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200'
        })
        
        # Update password fields for better styling
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200'
        })
    
    def clean_username(self):
        """Validação personalizada para o campo username"""
        username = self.cleaned_data.get('username')
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        
        return username
    
    def clean_email(self):
        """Validação personalizada para o campo email"""
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado no sistema.')
        
        return email
    
    def clean_first_name(self):
        """Validação personalizada para o campo first_name"""
        first_name = self.cleaned_data.get('first_name')
        
        if not first_name or not first_name.strip():
            raise forms.ValidationError('Nome é obrigatório.')
        
        # Check for reasonable length
        if len(first_name.strip()) < 2:
            raise forms.ValidationError('Nome deve ter pelo menos 2 caracteres.')
        
        return first_name.strip()
    
    def clean_last_name(self):
        """Validação personalizada para o campo last_name"""
        last_name = self.cleaned_data.get('last_name')
        
        if not last_name or not last_name.strip():
            raise forms.ValidationError('Sobrenome é obrigatório.')
        
        # Check for reasonable length
        if len(last_name.strip()) < 2:
            raise forms.ValidationError('Sobrenome deve ter pelo menos 2 caracteres.')
        
        return last_name.strip()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Criar ou atualizar o perfil - sempre como visualizador para novos registros
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.user_type = 'visualizador'  # Automaticamente configura como visualizador
            profile.department = self.cleaned_data.get('department')
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


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulário personalizado para alterar senha do usuário logado"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizar labels
        self.fields['old_password'].label = 'Senha Atual'
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password2'].label = 'Confirmar Nova Senha'
        
        # Adicionar classes CSS para Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200',
                'placeholder': self._get_placeholder(field_name)
            })
    
    def _get_placeholder(self, field_name):
        """Retorna placeholder apropriado para cada campo"""
        placeholders = {
            'old_password': 'Digite sua senha atual',
            'new_password1': 'Digite sua nova senha',
            'new_password2': 'Confirme sua nova senha'
        }
        return placeholders.get(field_name, '')