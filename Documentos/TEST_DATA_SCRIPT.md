# Script de População de Dados de Teste

Este script cria dados de teste completos para a aplicação EventoSys, incluindo eventos, relatórios e participantes para testar todas as funcionalidades do sistema.

## Estrutura do Script

O script está organizado nas seguintes seções:

1. **Configuração inicial e imports necessários**
2. **Função para gerar eventos únicos**
3. **Função para gerar eventos recorrentes**
4. **Função para gerar participantes e associações**
5. **Função para gerar dados de relatórios**
6. **Função principal que executa todas as operações**
7. **Tratamento de erros e logs**

## Como Executar

### Pré-requisitos

Antes de executar o script, certifique-se de:

1. Ter o ambiente virtual ativado:
   ```bash
   .venv\Scripts\activate
   ```

2. Ter executado as migrações do banco de dados:
   ```bash
   py manage.py migrate
   ```

3. Ter populado os dados iniciais:
   ```bash
   py manage.py populate_initial_data
   ```

### Execução do Script

Para popular o banco de dados com dados de teste:

```bash
py manage.py populate_test_data
```

Para limpar os dados de teste existentes e popular novamente:

```bash
py manage.py populate_test_data --clear
```

## Dados Gerados

### Eventos

O script gera três categorias de eventos:

1. **Eventos Únicos** (50 eventos):
   - Distribuídos nos últimos 3 meses e próximos 6 meses
   - Com diferentes status: planejado, em_andamento, concluido, cancelado
   - Com diferentes modalidades: presencial, virtual, híbrido
   - Com diferentes públicos-alvo

2. **Eventos Recorrentes**:
   - 3 eventos diários com 5 instâncias cada
   - 3 eventos semanais com 5 instâncias cada
   - 3 eventos mensais com 5 instâncias cada

### Participantes

- Cada evento recebe entre 3 e 10 participantes
- Os participantes são selecionados aleatoriamente dos usuários de teste
- Status de confirmação e presença são atribuídos aleatoriamente

### Relatórios

- 10 relatórios de teste de diferentes tipos:
  - Eventos por período
  - Eventos por tipo
  - Eventos por departamento
  - Eventos por status
  - Resumo de participantes
  - Uso de localizações
  - Resumo mensal
  - Resumo anual
- Formatos variados: PDF, Excel, CSV
- Configurações de agendamento aleatórias

## Verificação dos Dados

### Verificar Eventos

```bash
py manage.py shell
```

```python
from events.models import Event
print(f"Total de eventos: {Event.objects.count()}")
for event in Event.objects.filter(name__startswith='Teste')[:5]:
    print(f"- {event.name}: {event.start_datetime} ({event.status})")
```

### Verificar Relatórios

```bash
py manage.py shell
```

```python
from reports.models import Report
print(f"Total de relatórios: {Report.objects.count()}")
for report in Report.objects.filter(name__startswith='Relatório Teste')[:5]:
    print(f"- {report.name}: {report.report_type} ({report.format})")
```

### Verificar Participantes

```bash
py manage.py shell
```

```python
from events.models import EventParticipant
print(f"Total de participações: {EventParticipant.objects.count()}")
for participant in EventParticipant.objects.filter(event__name__startswith='Teste')[:5]:
    print(f"- {participant.user.username} em {participant.event.name}")
```

## Personalização

O script pode ser personalizado modificando os seguintes parâmetros:

- Número de eventos gerados (alterar os ranges nos loops)
- Intervalo de datas (modificar as variáveis de data)
- Tipos de eventos recorrentes (adicionar/remover do array)
- Número de participantes por evento (ajustar o range)

## Tratamento de Erros

O script inclui tratamento de erros para:

- Dados insuficientes (quando tipos de evento, locais ou departamentos não existem)
- Problemas de conexão com o banco de dados
- Erros de validação de dados
- Logs detalhados para depuração

Todos os erros são registrados no log do sistema e exibidos no console.