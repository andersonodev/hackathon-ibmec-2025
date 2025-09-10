# Conecta Voz - Plataforma de Feedback Organizacional

Este é um sistema completo para dar voz aos sentimentos dos colaboradores, medir o clima organizacional e promover um ambiente de trabalho mais saudável e transparente.

## 🏗️ Arquitetura

- **Backend**: Django + Django REST Framework (API RESTful)
- **Frontend**: React + TypeScript (SPA)
- **Banco de Dados**: SQLite (desenvolvimento)
- **Autenticação**: Token-based Authentication

## 🚀 Como Executar a Aplicação

### 1. Backend (Django)

```bash
# Navegar para a pasta do backend
cd backend

# Ativar o ambiente virtual
source venv/bin/activate

# Instalar dependências (se ainda não instalou)
pip install -r requirements.txt

# Executar migrações
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser

# Iniciar o servidor (porta 8001)
python manage.py runserver 8001
```

O backend estará disponível em: http://localhost:8001

### 2. Frontend (React)

```bash
# Navegar para a pasta do frontend
cd frontend

# Instalar dependências (se ainda não instalou)
npm install

# Iniciar o servidor de desenvolvimento (porta 3000)
npm start
```

O frontend estará disponível em: http://localhost:3000

## 🎯 Funcionalidades Implementadas

### ✅ Sistema de Autenticação
- Login/Logout com tokens
- Gestão de usuários com diferentes papéis:
  - **Colaborador**: Usuário padrão
  - **Diretoria**: Acesso a relatórios
  - **Admin**: Controle total

### ✅ Interface Responsiva
- **Sidebar colapsável** com navegação baseada no papel do usuário
- **Design minimalista** com cores da marca (#05c0cc)
- **Ícones consistentes** usando Lucide React
- **Layout responsivo** para desktop, tablet e mobile

### ✅ Páginas Implementadas
- **Login**: Autenticação com validação
- **Dashboard**: Visão geral personalizada
- **Páginas placeholder** para todas as funcionalidades:
  - Check-in de Humor
  - Voz & Relatos
  - Mural da Equipe
  - Conectas
  - Meu Conecta
  - Relatórios (Diretoria/Admin)
  - Administração (Admin)

### ✅ Conectividade Backend-Frontend
- **API Service** completo para comunicação
- **Context de Autenticação** gerenciando estado global
- **Interceptação de requisições** com tokens automáticos
- **Tratamento de erros** e redirecionamentos

## 🔧 Estrutura de Arquivos

### Backend
```
backend/
├── conecta_voz/          # Configurações principais
├── users/                # Gestão de usuários
├── mood/                 # Check-in de humor
├── voice/                # Sistema de relatos
├── connectas/            # Sistema de conectas
├── council/              # Conselho/escalação
├── mural/                # Mural da equipe
├── reports/              # Relatórios e métricas
├── audit/                # Auditoria
├── requirements.txt      # Dependências Python
└── manage.py
```

### Frontend
```
frontend/
├── src/
│   ├── components/       # Componentes reutilizáveis
│   │   ├── Sidebar.tsx   # Menu lateral
│   │   └── Layout.tsx    # Layout principal
│   ├── contexts/         # Contextos React
│   │   └── AuthContext.tsx
│   ├── pages/            # Páginas da aplicação
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── PlaceholderPage.tsx
│   ├── services/         # Comunicação com API
│   │   └── api.ts
│   ├── types/            # Tipos TypeScript
│   │   └── index.ts
│   └── App.tsx           # Componente principal
├── public/
│   └── conectavoz.svg    # Logo da aplicação
└── package.json
```

## 🎨 Design System

### Cores
- **Primária**: #05c0cc (Turquesa)
- **Primária Escura**: #048a94
- **Texto Principal**: #1f2937
- **Texto Secundário**: #6b7280
- **Fundo**: #f8fafc

### Componentes
- **Sidebar**: Menu lateral colapsável com animações suaves
- **Cards**: Interface limpa com sombras sutis
- **Formulários**: Campos com validação visual
- **Botões**: Estados hover e focus bem definidos

## 🔐 Autenticação e Permissões

### Níveis de Acesso
1. **Colaborador**: Funcionalidades básicas
2. **Diretoria**: + Relatórios e análises
3. **Admin**: + Administração completa

### Navegação Dinâmica
O menu lateral mostra apenas as opções disponíveis para cada papel de usuário.

## 🌐 APIs Disponíveis

### Autenticação
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/user/` - Dados do usuário atual

### Funcionalidades (Em desenvolvimento)
- `/api/v1/mood/` - Check-in de humor
- `/api/v1/voice/` - Sistema de relatos
- `/api/v1/connectas/` - Gestão de conectas
- `/api/v1/mural/` - Mural da equipe
- `/api/v1/reports/` - Relatórios e métricas

## 📱 Responsividade

A aplicação é totalmente responsiva:
- **Desktop**: Sidebar expandida (240px)
- **Tablet**: Sidebar colapsada (72px)
- **Mobile**: Sidebar ocultável

## 🔄 Próximos Passos

1. **Implementar as funcionalidades backend restantes**
2. **Criar as páginas frontend específicas**
3. **Adicionar sistema de notificações**
4. **Implementar upload de arquivos**
5. **Adicionar testes automatizados**
6. **Configurar deploy para produção**

## 🛠️ Tecnologias Utilizadas

### Backend
- Django 4.2+
- Django REST Framework
- SQLite
- Python 3.10+

### Frontend
- React 18
- TypeScript
- React Router DOM
- Lucide React (ícones)
- CSS Modules

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação da API em:
http://localhost:8001/api/docs/ (quando o backend estiver rodando)

---

**Status**: ✅ Backend e Frontend conectados e funcionando
**Versão**: 1.0.0
**Data**: Setembro 2025
