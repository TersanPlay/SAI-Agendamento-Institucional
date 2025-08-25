# EventoSys - Sistema de Gestão de Eventos Institucionais

Sistema completo para gestão de eventos institucionais desenvolvido em Django com design limpo e minimalista.

## 🚀 Funcionalidades Principais

- **Cadastro Completo de Eventos**: 18+ tipos de eventos com todos os campos necessários
- **Calendário Interativo**: Visualizações múltiplas (mensal, semanal, diária, lista)
- **Controle de Acesso**: 3 níveis de usuário (Administrador, Gestor, Visualizador)
- **Notificações Automáticas**: Sistema interno de alertas
- **Relatórios**: Exportação em PDF e Excel
- **Integrações**: Google Calendar, Outlook, ICS
- **Design Responsivo**: Interface limpa com Tailwind CSS

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 4.2+
- **Frontend**: Tailwind CSS, FullCalendar
- **Banco de Dados**: SQLite
- **Python**: 3.8+

## 📦 Instalação

### 1. Clonar o projeto
```bash
# O projeto já está na pasta atual
cd c:\Users\Play\pop
```

### 2. Criar ambiente virtual
```bash
py -m venv .venv
```

### 3. Ativar ambiente virtual
```bash
# Windows
.venv\Scripts\activate

# Windows (com ambiente limpo - recomendado)
activate_clean.bat

# Windows PowerShell
.\start_project.ps1

# Linux/Mac
source .venv/bin/activate
```

### 4. Instalar dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente
```bash
# O arquivo .env já está configurado para desenvolvimento
# Para produção, altere as configurações necessárias
```

### 6. Criar migrações
```bash
py manage.py makemigrations
```

### 7. Aplicar migrações
```bash
py manage.py migrate
```

### 8. Carregar dados iniciais
```bash
py manage.py populate_initial_data
```

### 9. (Opcional) Carregar dados de teste
```bash
py manage.py populate_test_data
```

Para limpar e regerar os dados de teste:
```bash
py manage.py populate_test_data --clear
```

### 10. Executar servidor
```bash
py manage.py runserver

.venv/bin/activate && py manage.py runserver
```

### 11. Acessar o sistema
Abra o navegador em: http://127.0.0.1:8000

## 🔑 Credenciais Padrão

- **Usuário**: admin
- **Senha**: admin123

## 👤 Credenciais de Teste

- **Usuários**: test_user_0 a test_user_9
- **Senha**: test123

## 📁 Estrutura do Projeto

```
eventosys/
├── eventosys/          # Configurações do projeto
├── events/             # App principal - gestão de eventos
├── accounts/           # App de usuários e autenticação
├── notifications/      # App de notificações
├── reports/            # App de relatórios
├── templates/          # Templates HTML
├── static/             # Arquivos estáticos
├── requirements.txt    # Dependências Python
├── manage.py          # Comando principal Django
└── README.md          # Este arquivo
```

## 👥 Tipos de Usuários

### Administrador
- Acesso total ao sistema
- Gerenciamento de usuários
- Criação e edição de todos os eventos
- Acesso a relatórios e logs

### Gestor
- Criação e edição de eventos
- Visualização de eventos do departamento
- Acesso a relatórios básicos

### Visualizador
- Visualização de eventos públicos
- Eventos onde é participante
- Funcionalidades limitadas de criação

## 📋 Funcionalidades Detalhadas

### Cadastro de Eventos
- 18 tipos diferentes de eventos
- Modalidades: presencial, virtual, híbrido
- Controle de status (planejado, em andamento, concluído, cancelado)
- Até 5 documentos/links por evento
- Histórico completo de alterações

### Calendário Interativo
- Visualizações: mensal, semanal, diária, lista
- Filtros avançados por tipo, departamento, status
- 15 cores diferentes para categorização
- Exportação em PDF e ICS

### Sistema de Notificações
- Alertas automáticos de criação/alteração
- Lembretes personalizáveis
- Notificações por tipo de evento

### Relatórios e Análises
- Relatórios por período, tipo, departamento
- Exportação em Excel e PDF
- Dashboard com métricas em tempo real

### Dados de Teste
- Eventos únicos e recorrentes (diários, semanais, mensais)
- Participantes com confirmações e presença
- Relatórios de diferentes tipos e formatos
- Dados distribuídos em períodos passados, presentes e futuros

## 🔧 Verificação da Instalação

Execute o script de verificação:
```bash
py verify_installation.py
```

## 🛡️ Verificação do Ambiente

Para verificar se o ambiente virtual está corretamente configurado:
```bash
# Ative o ambiente virtual primeiro
.venv\Scripts\activate

# Execute o script de verificação do ambiente
python verify_environment.py
```

## 🛡️ Boas Práticas de Ambiente

Para evitar conflitos de dependências:

1. **Sempre ative o ambiente virtual** antes de trabalhar no projeto
2. **Use o script `activate_clean.bat`** para garantir um ambiente limpo
3. **Não instale pacotes globalmente** fora do ambiente virtual
4. **Verifique se está no ambiente virtual** antes de executar comandos Python

Para verificar se está no ambiente virtual:
```bash
# O prompt deve mostrar (.venv) no início
(.venv) C:\caminho\para\seu\projeto>

# Ou verifique as variáveis de ambiente
where python
```

## 🚀 Próximos Passos

1. Personalize as configurações em `eventosys/settings.py`
2. Configure email real para notificações
3. Adicione mais departamentos conforme necessário
4. Configure backup automático do banco de dados
5. Implemente SSL para produção

## 📞 Suporte

Para dúvidas e suporte técnico, consulte a documentação interna ou entre em contato com a equipe de TI.

## 📄 Licença

Sistema desenvolvido para uso interno institucional.

---

**EventoSys** - Sistema de Gestão de Eventos Institucionais
Desenvolvido com ❤️ usando Django e Tailwind CSS
____________________________________________________________
Sistema de Agendamento Institucional (SAI)

SEGI – Sistema de Eventos e Gestão Institucional

SAGE – Sistema de Administração de Gestão de Eventos

SIAFI – Sistema de Agenda e Fiscalização de Eventos (um pouco mais robusto)

SAGEI – Sistema Avançado de Gestão de Eventos Institucionais

SIGAE – Sistema de Gestão e Agenda de Eventos

SGEI – Sistema de Gestão de Eventos Institucionais

GesEventos

Agenda Institucional

Plenário Digital

Sigei – Sistema Institucional de Gestão de Eventos

E-Eventos

Sistema de Agendamento Institucional (SAI)

Eventual 360 **Gostei desse** 