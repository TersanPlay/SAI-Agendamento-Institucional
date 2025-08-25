# Solução para o Problema de Permissão do Usuário Admin

## Problema Identificado

Ao fazer login como administrador na aplicação frontend, a permissão estava sendo definida como "visualizador" em vez de "administrador", resultando no bloqueio de muitas funcionalidades.

## Diagnóstico

1. Verificamos os usuários no sistema e confirmamos que existia um usuário chamado "admin"
2. Verificamos o papel (role) atribuído a este usuário e descobrimos que estava definido como "visualizador"
3. Confirmamos que o usuário não tinha um departamento atribuído

## Solução Aplicada

### 1. Correção do Papel do Usuário

Atualizamos o papel do usuário admin de "visualizador" para "administrador" executando o seguinte comando:

```bash
py manage.py shell -c "from django.contrib.auth.models import User; from accounts.models import UserProfile; user = User.objects.get(username='admin'); user.profile.user_type = 'administrador'; user.profile.save(); print('User role updated to administrator')"
```

### 2. Carga de Dados Iniciais

Carregamos os dados iniciais do sistema, incluindo departamentos, tipos de eventos e localizações:

```bash
py manage.py populate_initial_data
```

### 3. Atribuição de Departamento

Atribuímos um departamento ao usuário admin (escolhemos o primeiro departamento disponível):

```bash
py manage.py shell -c "from django.contrib.auth.models import User; from events.models import Department; user = User.objects.get(username='admin'); dept = Department.objects.first(); user.profile.department = dept; user.profile.save(); print(f'Assigned department {dept.name} to admin user')"
```

## Verificação

Após as correções, verificamos que o usuário admin agora possui:
- Papel: administrador
- Departamento: Assessoria de Imprensa

## Funcionalidades que Devem Estar Disponíveis Agora

Com o papel de administrador corretamente atribuído, você deve ter acesso a todas as funcionalidades do sistema, incluindo:

1. **Gerenciamento de Usuários**: Criar, editar e excluir usuários
2. **Gerenciamento de Eventos**: Criar, editar e excluir qualquer evento
3. **Relatórios**: Acesso completo a todos os relatórios
4. **Logs de Acesso**: Visualização dos logs de auditoria
5. **Gerenciamento de Departamentos**: Criar e editar departamentos
6. **Dashboard de Monitoramento**: Acesso ao dashboard com métricas completas

## Recomendações

1. **Faça logout e login novamente** para garantir que as mudanças tenham efeito
2. **Verifique as permissões** navegando pelas diferentes seções do sistema
3. **Se encontrar problemas adicionais**, verifique os logs de erro do Django

## Comandos Úteis para Verificação Futura

Para verificar o papel de um usuário:
```bash
py manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='admin'); print('User:', user.username); print('Role:', user.profile.user_type)"
```

Para verificar todos os usuários e seus papéis:
```bash
py manage.py shell -c "from django.contrib.auth.models import User; users = User.objects.all(); [print(f'{u.username} - {u.profile.user_type}') for u in users]"
```

## Considerações Finais

O problema foi causado por uma configuração incorreta do perfil do usuário admin. Isso pode ter ocorrido durante a criação inicial do usuário ou devido a um problema no processo de instalação. Agora que o papel foi corrigido, todas as funcionalidades administrativas devem estar disponíveis.