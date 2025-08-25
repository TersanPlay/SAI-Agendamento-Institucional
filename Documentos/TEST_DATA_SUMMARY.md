# Resumo dos Dados de Teste Gerados

## Visão Geral

O script `populate_test_data.py` criou com sucesso um conjunto abrangente de dados de teste para a aplicação EventoSys, incluindo:

- **10 usuários de teste** com diferentes papéis e departamentos
- **98 eventos de teste** distribuídos entre eventos únicos e recorrentes
- **10 relatórios de teste** de diferentes tipos e formatos
- **593 participações** em eventos de teste

## Detalhes dos Dados Gerados

### Usuários de Teste

Foram criados 10 usuários de teste com os seguintes padrões:
- Nome de usuário: `test_user_0` a `test_user_9`
- Senha padrão: `test123`
- Distribuição aleatória de papéis: administrador, gestor e visualizador
- Associação aleatória a departamentos existentes
- Números de telefone fictícios

### Eventos de Teste

#### Eventos Únicos (50 eventos)
- Distribuídos nos últimos 3 meses e próximos 6 meses
- Horários variados entre 8h e 18h
- Status variados: planejado, em andamento, concluído, cancelado
- Modalidades: presencial, virtual, híbrido
- Públicos-alvo: interno, externo, ambos

#### Eventos Recorrentes (48 eventos)
- 3 eventos diários com 5 instâncias cada (15 eventos)
- 3 eventos semanais com 5 instâncias cada (15 eventos)
- 3 eventos mensais com 5 instâncias cada (15 eventos)
- Evento base + instâncias individuais (3 eventos base)

### Relatórios de Teste

Foram criados 10 relatórios de teste com:
- Tipos variados: eventos por período, tipo, departamento, status, resumos mensais/anuais
- Formatos: PDF, Excel, CSV
- Períodos aleatórios nos últimos 6 meses
- Configurações de agendamento aleatórias

### Participantes

Cada evento de teste recebeu entre 3 e 10 participantes:
- Seleção aleatória dos usuários de teste
- Status de confirmação e presença atribuídos aleatoriamente
- Participações passadas marcadas como "compareceu" ou "não compareceu"

## Como Usar os Dados de Teste

### Acesso aos Usuários de Teste

Para fazer login como um usuário de teste:
1. Acesse a página de login
2. Use qualquer um dos nomes de usuário: `test_user_0` a `test_user_9`
3. Senha: `test123`

### Verificação dos Dados

Para verificar os dados gerados, execute:
```bash
py verify_test_data.py
```

### Limpeza dos Dados

Para remover os dados de teste e regerar:
```bash
py manage.py populate_test_data --clear
```

## Estrutura do Script

O script está organizado em funções modulares:

1. **clear_test_data()** - Remove dados de teste existentes
2. **create_test_users()** - Cria usuários de teste
3. **generate_unique_events()** - Gera eventos únicos
4. **generate_recurring_events()** - Gera eventos recorrentes
5. **generate_participants()** - Cria participações nos eventos
6. **generate_report_data()** - Gera dados de relatórios

## Personalização

O script pode ser facilmente personalizado modificando:
- Número de eventos gerados
- Intervalos de datas
- Distribuição de status e tipos
- Número de participantes por evento

## Tratamento de Erros

O script inclui tratamento robusto de erros:
- Verificação de dados mínimos necessários
- Logging detalhado
- Mensagens de erro claras para o console
- Continuidade da execução mesmo com erros parciais