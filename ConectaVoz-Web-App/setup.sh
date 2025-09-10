#!/bin/bash

# Script de inicialização do Conecta Voz
# Este script facilita o setup e execução da aplicação

echo "🚀 Iniciando Conecta Voz..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Execute este script na raiz do projeto (onde estão as pastas backend e frontend)"
    exit 1
fi

print_status "Verificando pré-requisitos..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Instale Python 3.8 ou superior."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js não encontrado. Instale Node.js 16 ou superior."
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    print_error "npm não encontrado. Instale npm junto com Node.js."
    exit 1
fi

print_success "Pré-requisitos verificados!"

# Setup do Backend
print_status "Configurando backend..."

cd backend

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    print_status "Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
print_status "Instalando dependências Python..."
pip install -r requirements.txt

# Executar migrações
print_status "Executando migrações do banco de dados..."
python manage.py migrate

# Verificar se existe superusuário
print_status "Verificando usuário administrador..."
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('admin exists' if User.objects.filter(username='admin').exists() else 'no admin')" | grep -q "admin exists"; then
    print_warning "Superusuário 'admin' não encontrado."
    echo "Criando superusuário padrão..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@conectavoz.com.br', 'admin123')" | python manage.py shell
    print_success "Superusuário criado! Login: admin | Senha: admin123"
fi

cd ..

# Setup do Frontend
print_status "Configurando frontend..."

cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    print_status "Instalando dependências Node.js..."
    npm install
else
    print_status "Dependências Node.js já instaladas."
fi

cd ..

print_success "Setup concluído!"

echo
echo "=========================================="
echo "🎯 Conecta Voz - Pronto para usar!"
echo "=========================================="
echo
echo "Para iniciar a aplicação:"
echo
echo "1️⃣  Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver 8001"
echo
echo "2️⃣  Frontend (Terminal 2):"
echo "   cd frontend" 
echo "   npm start"
echo
echo "🌐 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   API Docs: http://localhost:8001/api/docs/"
echo
echo "👤 Credenciais de teste:"
echo "   Admin:    admin / admin123"
echo "   Diretora: diretora.ana / diretoria123"
echo "   Colaborador: bruno.mendes / colab123"
echo
echo "=========================================="
