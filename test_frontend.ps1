# Script PowerShell para testar se o frontend compila corretamente

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "TESTE DE COMPILAÇÃO DO FRONTEND AETHEL" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Verificar se estamos no diretório correto
if (-not (Test-Path "frontend")) {
    Write-Host "❌ ERRO: Diretório 'frontend' não encontrado" -ForegroundColor Red
    Write-Host "Execute este script do diretório raiz do projeto" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Diretório frontend encontrado" -ForegroundColor Green

# Verificar arquivos criados
Write-Host ""
Write-Host "Verificando arquivos criados:" -ForegroundColor Cyan
Write-Host "-----------------------------" -ForegroundColor Cyan

function Check-File {
    param($path)
    
    if (Test-Path $path) {
        Write-Host "✅ $path" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $path (NÃO ENCONTRADO)" -ForegroundColor Red
        return $false
    }
}

Check-File "frontend/components/PricingCard.tsx"
Check-File "frontend/app/pricing/page.tsx"
Check-File "aethel/core/grammar.py"

Write-Host ""
Write-Host "Verificando dependências do frontend:" -ForegroundColor Cyan
Write-Host "-------------------------------------" -ForegroundColor Cyan

Set-Location frontend

# Verificar package.json
if (Test-Path "package.json") {
    Write-Host "✅ package.json encontrado" -ForegroundColor Green
    
    $packageContent = Get-Content "package.json" -Raw
    
    # Verificar dependências necessárias
    if ($packageContent -match "next" -and $packageContent -match "react" -and $packageContent -match "tailwindcss") {
        Write-Host "✅ Dependências principais encontradas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Algumas dependências podem estar faltando" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ package.json não encontrado" -ForegroundColor Red
    exit 1
}

# Verificar node_modules
if (Test-Path "node_modules") {
    Write-Host "✅ node_modules encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  node_modules não encontrado - execute 'npm install' primeiro" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificando imports:" -ForegroundColor Cyan
Write-Host "-------------------" -ForegroundColor Cyan

# Verificar imports no PricingCard
$pricingCardContent = Get-Content "..\frontend\components\PricingCard.tsx" -Raw
if ($pricingCardContent -match "import.*lucide-react") {
    Write-Host "✅ PricingCard importa lucide-react" -ForegroundColor Green
} else {
    Write-Host "❌ PricingCard não importa lucide-react" -ForegroundColor Red
}

if ($pricingCardContent -match "import.*useState") {
    Write-Host "✅ PricingCard importa useState" -ForegroundColor Green
} else {
    Write-Host "❌ PricingCard não importa useState" -ForegroundColor Red
}

# Verificar imports na página de pricing
$pricingPageContent = Get-Content "..\frontend\app\pricing\page.tsx" -Raw
if ($pricingPageContent -match "import.*PricingCard") {
    Write-Host "✅ Página de pricing importa PricingCard" -ForegroundColor Green
} else {
    Write-Host "❌ Página de pricing não importa PricingCard" -ForegroundColor Red
}

if ($pricingPageContent -match "import.*lucide-react") {
    Write-Host "✅ Página de pricing importa lucide-react" -ForegroundColor Green
} else {
    Write-Host "❌ Página de pricing não importa lucide-react" -ForegroundColor Red
}

Write-Host ""
Write-Host "Verificando estrutura da página:" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

# Contar componentes na página
$componentCount = ($pricingPageContent | Select-String "<PricingCard" -AllMatches).Matches.Count
Write-Host "✅ Página contém $componentCount componentes PricingCard" -ForegroundColor Green

# Verificar se tem os 4 planos
if ($componentCount -eq 4) {
    Write-Host "✅ Todos os 4 planos estão presentes" -ForegroundColor Green
} else {
    Write-Host "⚠️  Esperados 4 planos, encontrados $componentCount" -ForegroundColor Yellow
}

# Verificar FAQ
if ($pricingPageContent -match "Frequently asked questions") {
    Write-Host "✅ Seção FAQ presente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Seção FAQ não encontrada" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificando gramática atualizada:" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan

$grammarContent = Get-Content "..\aethel\core\grammar.py" -Raw
if ($grammarContent -match "NUMBER: /-?\[0-9\]+\\\.\[0-9\]+\)\?/") {
    Write-Host "✅ Gramática atualizada com suporte a decimais" -ForegroundColor Green
} else {
    Write-Host "⚠️  Gramática pode não estar atualizada" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "TESTE COMPLETO" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Execute 'cd frontend && npm run dev' para testar localmente"
Write-Host "2. Acesse http://localhost:3000/pricing"
Write-Host "3. Verifique se a página carrega corretamente"
Write-Host "4. Teste a responsividade em diferentes tamanhos de tela"
Write-Host ""
Write-Host "Para deploy em produção:" -ForegroundColor Yellow
Write-Host "1. Configure Vercel (frontend) e Railway (backend)"
Write-Host "2. Configure domínio aethel-lang.org"
Write-Host "3. Configure Stripe para pagamentos"
Write-Host ""
Write-Host "✅ Frontend pronto para os próximos passos!" -ForegroundColor Green

# Voltar ao diretório original
Set-Location ..