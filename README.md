# AgendaFácil

Sistema web de agendamento online gratuito para pequenos prestadores de serviços.

Desenvolvido como Projeto Integrador em Computação III (PJI310) da UNIVESP.

🔗 **[Acesse o sistema](https://agendafacil-bzbf.onrender.com)**

---

## 📋 Sobre o Projeto

O AgendaFácil surgiu como resposta à exclusão digital enfrentada por pequenos prestadores de serviços — cabeleireiros, manicures, esteticistas e outros profissionais que ainda dependem de WhatsApp, ligações telefônicas e agendas de papel para gerenciar seus atendimentos.

O sistema foi desenvolvido a partir das necessidades identificadas junto ao **Salão Beleza & Charme**, estabelecimento de beleza de pequeno porte localizado em Porto Alegre/RS, e oferece uma plataforma gratuita que automatiza o processo de agendamento online.

---

## ✨ Funcionalidades

### Para o Cliente
- Cadastro e login com opção "Lembrar de mim"
- Listagem de prestadores disponíveis
- Agendamento em 4 etapas: prestador → serviço → data → horário
- Calendário navegável com limite de 60 dias
- Cálculo automático de horários disponíveis por profissional
- Visualização de agendamentos (Próximos, Realizados e Cancelados)
- Cancelamento de agendamentos futuros
- Edição de perfil e alteração de senha

### Para o Prestador
- Dashboard com indicadores em tempo real (agendamentos hoje, pendentes, clientes na semana, serviços cadastrados)
- Agenda navegável por data com confirmação e cancelamento de agendamentos
- Gerenciamento completo de serviços (cadastro, edição, ativação/desativação, exclusão)
- Módulo de bloqueios de agenda por profissional (com validação de conflitos)
- Edição de perfil, dados do negócio, endereço e horários de funcionamento

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3 + Django 6 |
| Banco de dados | PostgreSQL (Supabase) |
| Frontend | HTML5 + Bootstrap 5 + JavaScript |
| API REST | Django REST Framework |
| API externa | ViaCEP (preenchimento automático de endereço) |
| Autenticação | Customizada com PBKDF2-SHA256 |
| Controle de versão | Git + GitHub |
| CI/CD | GitHub Actions |
| Deploy | Render |
| Monitoramento | UptimeRobot |

---

## 🏗️ Arquitetura

O sistema segue o padrão arquitetural **MTV (Model-Template-View)** do Django, com banco de dados relacional PostgreSQL hospedado no Supabase.

### Modelos principais

- **Usuario** — credenciais de acesso e tipo de perfil (cliente/prestador)
- **Prestador** — dados do negócio, endereço e horários de funcionamento
- **Servico** — catálogo de serviços com nome, descrição, duração, preço e profissional responsável
- **Agendamento** — registro de agendamentos com status (pendente/confirmado/cancelado)
- **Bloqueio** — indisponibilidades de agenda por profissional

### API REST

Endpoints disponíveis:
- `GET /api/prestadores/` — listagem de prestadores
- `GET /api/servicos/<id>/` — serviços de um prestador
- `GET /api/horarios/<prestador_id>/<servico_id>/<data>/` — horários disponíveis

---

## ⚙️ Lógica de Disponibilidade

O cálculo de horários disponíveis é um dos principais diferenciais do sistema. A agenda é controlada em **slots de 15 minutos por profissional**, garantindo que:

- Agendamentos de diferentes serviços realizados pela mesma profissional não se sobreponham
- Bloqueios de agenda sejam respeitados no cálculo de disponibilidade
- O cliente visualize apenas os horários com janela suficiente para a duração do serviço selecionado

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.12+
- PostgreSQL

### Instalação

```bash
# Clone o repositório
git clone https://github.com/richardpontes/agendafacil.git
cd agendafacil

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
# Crie um arquivo .env na raiz com:
# SECRET_KEY=sua-chave-secreta
# DEBUG=True
# DB_NAME=nome-do-banco
# DB_USER=usuario
# DB_PASSWORD=senha
# DB_HOST=host
# DB_PORT=5432

# Execute as migrações
python manage.py migrate

# Inicie o servidor
python manage.py runserver
```

---

## 🧪 Testes

O projeto possui 12 testes automatizados cobrindo os principais fluxos de autenticação, executados automaticamente a cada commit via GitHub Actions.

```bash
python manage.py test
```

---

## ⚠️ Limitações Conhecidas

- **Agenda por profissional**: o sistema atual utiliza um campo `profissional` no cadastro de serviços como simplificação. A implementação completa, com cadastro de profissionais e vinculação aos serviços, está prevista como melhoria futura.
- **Slots fixos**: os horários são calculados em slots de 15 minutos. Serviços com durações não múltiplas de 15 minutos podem gerar pequenas janelas ociosas na agenda.
- **Sidebar replicada**: o componente de navegação lateral é replicado em cada template. A refatoração com `{% include %}` está prevista como melhoria futura.

---

## 🔮 Melhorias Futuras

- Cadastro de profissionais vinculados aos serviços
- Gerenciamento de agenda por profissional com acesso individual
- Notificações automáticas por e-mail (confirmação, lembrete, cancelamento)
- Slots dinâmicos baseados na disponibilidade real da profissional
- Histórico e relatórios para o prestador
- Upload de foto de perfil

---

## 👥 Equipe

Projeto desenvolvido por alunos dos cursos de **Ciência de Dados** e **Engenharia de Computação** da **UNIVESP**.

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como requisito do Projeto Integrador em Computação III (PJI310) da UNIVESP.
