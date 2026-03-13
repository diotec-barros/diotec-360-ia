#!/bin/bash
# Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash
# Script para testar se o frontend compila corretamente

echo "========================================="
echo "TESTE DE COMPILAÇÃO DO FRONTEND AETHEL"
echo "========================================="

# Verificar se estamos no diretório correto
if [ ! -d "frontend" ]; then
    echo "❌ ERRO: Diretório 'frontend' não encontrado"
    echo "Execute este script do diretório raiz do projeto"
    exit 1
fi

echo "✅ Diretório frontend encontrado"

# Verificar arquivos criados
echo ""
echo "Verificando arquivos criados:"
echo "-----------------------------"

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1 (NÃO ENCONTRADO)"
        return 1
    fi
}

check_file "frontend/components/PricingCard.tsx"
check_file "frontend/app/pricing/page.tsx"
check_file "aethel/core/grammar.py"

echo ""
echo "Verificando dependências do frontend:"
echo "-------------------------------------"

cd frontend

# Verificar package.json
if [ -f "package.json" ]; then
    echo "✅ package.json encontrado"
    
    # Verificar dependências necessárias
    if grep -q "next" package.json && grep -q "react" package.json && grep -q "tailwindcss" package.json; then
        echo "✅ Dependências principais encontradas"
    else
        echo "⚠️  Algumas dependências podem estar faltando"
    fi
else
    echo "❌ package.json não encontrado"
    exit 1
fi

# Verificar node_modules
if [ -d "node_modules" ]; then
    echo "✅ node_modules encontrado"
else
    echo "⚠️  node_modules não encontrado - execute 'npm install' primeiro"
fi

echo ""
echo "Testando TypeScript compilation:"
echo "--------------------------------"

# Verificar se TypeScript está instalado
if npx tsc --version > /dev/null 2>&1; then
    echo "✅ TypeScript instalado"
    
    # Tentar compilar apenas os arquivos novos
    echo "Compilando componentes novos..."
    
    # Compilar PricingCard
    if npx tsc --noEmit --jsx react-jsx frontend/components/PricingCard.tsx 2>/dev/null; then
        echo "✅ PricingCard.tsx compila sem erros"
    else
        echo "❌ Erro na compilação do PricingCard.tsx"
        npx tsc --noEmit --jsx react-jsx frontend/components/PricingCard.tsx 2>&1 | head -20
    fi
    
    # Compilar página de pricing
    if npx tsc --noEmit --jsx react-jsx frontend/app/pricing/page.tsx 2>/dev/null; then
        echo "✅ pricing/page.tsx compila sem erros"
    else
        echo "❌ Erro na compilação do pricing/page.tsx"
        npx tsc --noEmit --jsx react-jsx frontend/app/pricing/page.tsx 2>&1 | head -20
    fi
    
else
    echo "⚠️  TypeScript não encontrado - pulando verificação de tipos"
fi

echo ""
echo "Verificando imports:"
echo "-------------------"

# Verificar imports no PricingCard
if grep -q "import.*lucide-react" frontend/components/PricingCard.tsx; then
    echo "✅ PricingCard importa lucide-react"
else
    echo "❌ PricingCard não importa lucide-react"
fi

if grep -q "import.*useState" frontend/components/PricingCard.tsx; then
    echo "✅ PricingCard importa useState"
else
    echo "❌ PricingCard não importa useState"
fi

# Verificar imports na página de pricing
if grep -q "import.*PricingCard" frontend/app/pricing/page.tsx; then
    echo "✅ Página de pricing importa PricingCard"
else
    echo "❌ Página de pricing não importa PricingCard"
fi

if grep -q "import.*lucide-react" frontend/app/pricing/page.tsx; then
    echo "✅ Página de pricing importa lucide-react"
else
    echo "❌ Página de pricing não importa lucide-react"
fi

echo ""
echo "Verificando estrutura da página:"
echo "--------------------------------"

# Contar componentes na página
component_count=$(grep -c "<PricingCard" frontend/app/pricing/page.tsx)
echo "✅ Página contém $component_count componentes PricingCard"

# Verificar se tem os 4 planos
if [ "$component_count" -eq 4 ]; then
    echo "✅ Todos os 4 planos estão presentes"
else
    echo "⚠️  Esperados 4 planos, encontrados $component_count"
fi

# Verificar FAQ
faq_count=$(grep -c "Frequently asked questions" frontend/app/pricing/page.tsx)
if [ "$faq_count" -gt 0 ]; then
    echo "✅ Seção FAQ presente"
else
    echo "⚠️  Seção FAQ não encontrada"
fi

echo ""
echo "========================================="
echo "TESTE COMPLETO"
echo "========================================="
echo ""
echo "Próximos passos:"
echo "1. Execute 'cd frontend && npm run dev' para testar localmente"
echo "2. Acesse http://localhost:3000/pricing"
echo "3. Verifique se a página carrega corretamente"
echo "4. Teste a responsividade em diferentes tamanhos de tela"
echo ""
echo "Para deploy em produção:"
echo "1. Configure Vercel (frontend) e Railway (backend)"
echo "2. Configure domínio diotec360-lang.org"
echo "3. Configure Stripe para pagamentos"
echo ""
echo "✅ Frontend pronto para os próximos passos!"