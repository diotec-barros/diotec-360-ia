# ===========================================================================
# CONFIGURAÇÃO RÁPIDA - AMBIENTE SANDBOX
# ===========================================================================
# Prepara o ambiente para testes com PayPal Sandbox
# ===========================================================================

Write-Host "🧪 CONFIGURAÇÃO DE AMBIENTE SANDBOX - DIOTEC 360" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Verifica se os arquivos existem
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env.sandbox")) {
    Write-Host "❌ Arquivo .env.sandbox não encontrado!" -ForegroundColor Red
    exit 1
}

# Pergunta se deseja fazer backup
Write-Host "📋 Passo 1: Backup do .env atual" -ForegroundColor Yellow
$backup = Read-Host "Deseja fazer backup do .env atual? (S/N)"

if ($backup -eq "S" -or $backup -eq "s") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item .env ".env.backup_$timestamp"
    Write-Host "✅ Backup criado: .env.backup_$timestamp" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Passo 2: Configurar variáveis" -ForegroundColor Yellow
Write-Host ""

# Solicita o HF_TOKEN
Write-Host "🧠 Hugging Face Token:" -ForegroundColor Cyan
$hfToken = Read-Host "Cole seu HF_TOKEN (ou Enter para pular)"

# Solicita o Webhook ID
Write-Host ""
Write-Host "🔗 PayPal Webhook ID (Sandbox):" -ForegroundColor Cyan
$webhookId = Read-Host "Cole seu PAYPAL_WEBHOOK_ID do sandbox (ou Enter para pular)"

# Copia o .env.sandbox para .env
Write-Host ""
Write-Host "📋 Passo 3: Aplicando configuração sandbox..." -ForegroundColor Yellow
Copy-Item .env.sandbox .env

# Atualiza os valores se fornecidos
if ($hfToken) {
    $content = Get-Content .env -Raw
    $content = $content -replace 'HF_TOKEN=COLE_AQUI_O_SEU_TOKEN_HF', "HF_TOKEN=$hfToken"
    $content | Set-Content .env -NoNewline
    Write-Host "✅ HF_TOKEN configurado" -ForegroundColor Green
}

if ($webhookId) {
    $content = Get-Content .env -Raw
    $content = $content -replace 'PAYPAL_WEBHOOK_ID=CRIAR_WEBHOOK_NO_SANDBOX', "PAYPAL_WEBHOOK_ID=$webhookId"
    $content | Set-Content .env -NoNewline
    Write-Host "✅ PAYPAL_WEBHOOK_ID configurado" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ AMBIENTE SANDBOX CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""

Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Iniciar o backend:" -ForegroundColor White
Write-Host "   cd api" -ForegroundColor Gray
Write-Host "   python -m uvicorn main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Iniciar o frontend (em outro terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Acessar: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "4. Realizar teste de pagamento com conta sandbox" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Modo: SANDBOX (dinheiro fake)" -ForegroundColor Yellow
Write-Host "🏛️ THE MONOLITH IS READY FOR TESTING" -ForegroundColor Cyan
