# ===========================================================================
# DIOTEC 360 IA - Validador de Configuração .env
# ===========================================================================
# Script para verificar se o arquivo .env está corretamente preenchido
# Desenvolvido por: Kiro para Dionísio Sebastião Barros
# ===========================================================================

Write-Host ""
Write-Host "🏛️ DIOTEC 360 IA - Validador de Configuração" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "❌ ERRO: Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "   Execute: Copy-Item .env.example .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
Write-Host ""

# Função para verificar variável
function Test-EnvVar {
    param(
        [string]$VarName,
        [string]$Description,
        [string]$Pattern = "",
        [bool]$Required = $true
    )
    
    $line = Get-Content .env | Where-Object { $_ -match "^$VarName=" }
    
    if (-not $line) {
        if ($Required) {
            Write-Host "❌ $Description" -ForegroundColor Red
            Write-Host "   Variável $VarName não encontrada" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host "⚠️  $Description (opcional)" -ForegroundColor Yellow
            return $true
        }
    }
    
    $value = ($line -split "=", 2)[1].Trim('"').Trim("'")
    
    # Verificar se está vazio
    if ([string]::IsNullOrWhiteSpace($value)) {
        if ($Required) {
            Write-Host "❌ $Description" -ForegroundColor Red
            Write-Host "   Variável $VarName está vazia" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host "⚠️  $Description (vazio, mas opcional)" -ForegroundColor Yellow
            return $true
        }
    }
    
    # Verificar se contém placeholder
    if ($value -match "COLE_AQUI|GERE_UMA|your-|SEU_") {
        Write-Host "❌ $Description" -ForegroundColor Red
        Write-Host "   Valor ainda é placeholder: $value" -ForegroundColor Yellow
        return $false
    }
    
    # Verificar padrão se fornecido
    if ($Pattern -and $value -notmatch $Pattern) {
        Write-Host "⚠️  $Description" -ForegroundColor Yellow
        Write-Host "   Valor não corresponde ao padrão esperado" -ForegroundColor Yellow
        Write-Host "   Valor: $($value.Substring(0, [Math]::Min(20, $value.Length)))..." -ForegroundColor Gray
        return $true  # Aviso, não erro
    }
    
    Write-Host "✅ $Description" -ForegroundColor Green
    return $true
}

# Contador de problemas
$issues = 0

Write-Host "🔍 Verificando Configurações Críticas..." -ForegroundColor Cyan
Write-Host ""

# Identidade
Write-Host "📋 Identidade Soberana:" -ForegroundColor White
if (-not (Test-EnvVar "DIOTEC360_CREATOR" "Creator Name")) { $issues++ }
if (-not (Test-EnvVar "DIOTEC360_ORG" "Organization Name")) { $issues++ }
Write-Host ""

# PayPal
Write-Host "💳 PayPal Configuration:" -ForegroundColor White
if (-not (Test-EnvVar "PAYPAL_CLIENT_ID" "PayPal Client ID" "^A[A-Za-z0-9_-]+$")) { $issues++ }
if (-not (Test-EnvVar "PAYPAL_SECRET" "PayPal Secret" "^E[A-Za-z0-9_-]+$")) { $issues++ }
if (-not (Test-EnvVar "PAYPAL_MODE" "PayPal Mode" "^(sandbox|live)$")) { $issues++ }
if (-not (Test-EnvVar "PAYPAL_WEBHOOK_ID" "PayPal Webhook ID" "^WH-" $false)) { $issues++ }
Write-Host ""

# Hugging Face
Write-Host "🧠 Hugging Face Configuration:" -ForegroundColor White
if (-not (Test-EnvVar "HF_TOKEN" "Hugging Face Token" "^hf_[A-Za-z0-9]+$")) { $issues++ }
Write-Host ""

# Alpha Vantage
Write-Host "📈 Alpha Vantage Configuration:" -ForegroundColor White
if (-not (Test-EnvVar "ALPHA_VANTAGE_API_KEY" "Alpha Vantage API Key" "" $false)) { $issues++ }
Write-Host ""

# Segurança
Write-Host "🔐 Security Configuration:" -ForegroundColor White
if (-not (Test-EnvVar "DIOTEC360_SECRET_KEY" "Secret Key" "^[A-Za-z0-9]{32,}$")) { $issues++ }
Write-Host ""

# Infraestrutura
Write-Host "🌐 Infrastructure Configuration:" -ForegroundColor White
if (-not (Test-EnvVar "NEXT_PUBLIC_API_URL" "API URL" "^https://")) { $issues++ }
if (-not (Test-EnvVar "DIOTEC360_CORS_ORIGINS" "CORS Origins" "^https://")) { $issues++ }
Write-Host ""

# Resultado Final
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

if ($issues -eq 0) {
    Write-Host "🎉 SUCESSO! Configuração válida!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Todas as variáveis críticas estão configuradas" -ForegroundColor Green
    Write-Host "✅ Nenhum placeholder detectado" -ForegroundColor Green
    Write-Host "✅ Padrões de formato validados" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Próximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Fazer backup do .env em local seguro" -ForegroundColor White
    Write-Host "   2. Configurar as mesmas variáveis no Hugging Face" -ForegroundColor White
    Write-Host "   3. Testar o webhook do PayPal" -ForegroundColor White
    Write-Host "   4. Fazer deploy!" -ForegroundColor White
    Write-Host ""
    Write-Host "⚖️ THE MONOLITH IS READY" -ForegroundColor Magenta
    exit 0
} else {
    Write-Host "⚠️  ATENÇÃO: $issues problema(s) encontrado(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Ações necessárias:" -ForegroundColor Cyan
    Write-Host "   1. Revise as variáveis marcadas com ❌" -ForegroundColor White
    Write-Host "   2. Consulte GUIA_PREENCHIMENTO_ENV.md" -ForegroundColor White
    Write-Host "   3. Preencha os valores corretos" -ForegroundColor White
    Write-Host "   4. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Dica: Use 'Get-Content .env | Select-String VARIAVEL' para verificar valores" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
