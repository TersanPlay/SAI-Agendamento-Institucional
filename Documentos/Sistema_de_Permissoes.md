# Sistema de Permissões do EventoSys

## Visão Geral

O sistema de permissões do EventoSys é baseado em níveis de acesso com três papéis distintos: **Administrador**, **Gestor** e **Visualizador**. A implementação utiliza uma combinação de modelos estendidos do usuário, métodos de verificação de permissões, middleware de segurança e decorators para controlar o acesso às funcionalidades do sistema.

## Níveis de Acesso

### 1. Administrador
- **Permissões completas** sobre todo o sistema
- Pode criar, editar e excluir qualquer evento
- Pode gerenciar usuários (criar, editar, excluir)
- Pode visualizar todos os relatórios
- Pode acessar logs de auditoria
- Pode gerenciar departamentos

### 2. Gestor
- Pode criar e editar eventos
- Pode visualizar eventos do seu departamento
- Pode acessar relatórios básicos
- Pode visualizar eventos públicos
- Pode editar eventos que criou ou é responsável

### 3. Visualizador
- Pode visualizar eventos públicos
- Pode visualizar eventos onde é participante
- Pode visualizar eventos que criou
- Funcionalidades limitadas de criação
- Pode editar apenas eventos que criou (se tiver permissão)

## Implementação Técnica

### 1. Modelo de Usuário Estendido

O sistema utiliza o modelo `UserProfile` para estender o usuário padrão do Django:

```python
class UserProfile(models.Model):
    USER_TYPES = [
        ('administrador', 'Administrador'),
        ('gestor', 'Gestor'),
        ('visualizador', 'Visualizador'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='visualizador')
```

### 2. Métodos de Verificação de Permissões

O modelo `UserProfile` inclui métodos para verificar permissões específicas:

- `can_create_events()` - Verifica se o usuário pode criar eventos
- `can_edit_all_events()` - Verifica se pode editar todos os eventos
- `can_view_all_events()` - Verifica se pode visualizar todos os eventos
- `can_view_reports()` - Verifica se pode acessar relatórios

### 3. Funções de Utilidade para Permissões

O arquivo `accounts/utils.py` contém funções auxiliares para verificação de permissões:

- `has_permission()` - Verifica permissões genéricas
- `can_edit_event()` - Verifica se um usuário pode editar um evento específico
- `can_view_event()` - Verifica se um usuário pode visualizar um evento específico
- `get_user_accessible_events()` - Retorna eventos acessíveis ao usuário

### 4. Controle de Acesso nas Views

As views utilizam verificações de permissão diretamente no código:

```python
@login_required
def access_logs_view(request):
    """View para visualizar logs de acesso (apenas administradores)"""
    if not request.user.profile.is_administrator:
        messages.error(request, 'Acesso negado.')
        return redirect('events:dashboard')
```

### 5. Middleware de Segurança

O middleware `SecurityLoggingMiddleware` registra todas as ações dos usuários e pode aplicar limites de taxa para usuários não autenticados.

### 6. Formulários com Controle de Permissões

Os formulários diferenciam campos e opções com base no tipo de usuário, especialmente no formulário de registro onde o tipo de usuário é definido.

## Fluxo de Trabalho de Permissões

1. **Autenticação**: O usuário faz login no sistema
2. **Identificação do Papel**: O sistema identifica o tipo de usuário através do `UserProfile`
3. **Verificação de Permissões**: Antes de executar qualquer ação, o sistema verifica se o usuário tem permissão
4. **Registro de Ações**: Todas as ações são registradas no log de auditoria
5. **Aplicação de Restrições**: A interface e as funcionalidades são filtradas com base nas permissões

## Exemplos de Implementação

### Verificação de Permissão em Views
```python
@login_required
def user_management_view(request):
    if not request.user.profile.is_administrator:
        messages.error(request, 'Acesso negado.')
        return redirect('events:dashboard')
    # Código para gerenciamento de usuários
```

### Verificação de Permissão em Modelos
```python
@property
def can_create_events(self):
    """Administradores e gestores podem criar eventos"""
    return self.user_type in ['administrador', 'gestor']
```

### Verificação de Permissão em Utilitários
```python
def can_edit_event(user, event):
    """Verifica se o usuário pode editar um evento específico"""
    if profile.is_administrator:
        return True
    # Lógica específica para gestores e visualizadores
```

## Boas Práticas Implementadas

1. **Princípio do Menor Privilégio**: Cada papel tem apenas as permissões necessárias
2. **Verificação em Múltiplos Níveis**: Permissões verificadas tanto no frontend quanto no backend
3. **Auditoria**: Todas as ações são registradas para fins de auditoria
4. **Extensibilidade**: Sistema fácil de estender com novos papéis ou permissões
5. **Segurança**: Proteção contra acesso não autorizado em todas as camadas

## Considerações de Segurança

- Todas as verificações de permissão são feitas no backend
- O middleware registra todas as ações sensíveis
- Usuários não autenticados têm acesso limitado apenas a eventos públicos
- Há proteção contra ataques de força bruta com limitação de taxa