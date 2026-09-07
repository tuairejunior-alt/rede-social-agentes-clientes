#!/bin/bash

# Script para verificar e corrigir a instalação completa
# Rede Social - Agentes e Clientes

echo "=========================================="
echo "🔧 INICIANDO VERIFICAÇÃO E CORREÇÃO"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Backend
echo -e "${YELLOW}📦 Verificando Backend...${NC}"
if [ -d "backend" ]; then
    cd backend
    
    # Criar venv se não existir
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv
    fi
    
    # Ativar venv
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
    
    # Instalar dependências
    echo "Instalando dependências Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Verificar .env
    if [ ! -f ".env" ]; then
        echo "Criando arquivo .env..."
        cp .env.example .env
    fi
    
    echo -e "${GREEN}✅ Backend pronto!${NC}"
    cd ..
else
    echo -e "${RED}❌ Diretório backend não encontrado!${NC}"
fi

echo ""

# 2. Frontend
echo -e "${YELLOW}📦 Verificando Frontend...${NC}"
if [ -d "frontend" ]; then
    cd frontend
    
    # Limpar cache
    echo "Limpando cache npm..."
    rm -rf node_modules package-lock.json
    
    # Instalar dependências
    echo "Instalando dependências Node..."
    npm install
    
    # Verificar .env
    if [ ! -f ".env" ]; then
        echo "Criando arquivo .env..."
        cp .env.example .env
    fi
    
    echo -e "${GREEN}✅ Frontend pronto!${NC}"
    cd ..
else
    echo -e "${RED}❌ Diretório frontend não encontrado!${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ VERIFICAÇÃO COMPLETA!${NC}"
echo "=========================================="
echo ""
echo "🚀 Para iniciar a aplicação:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Acesse: http://localhost:3000"
echo ""
