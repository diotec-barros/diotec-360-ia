# ===========================================================================
# VALIDADOR DE CONFIGURAÇÃO SANDBOX
# ===========================================================================

Write-Host "Validador de Configuracao Sandbox - DIOTEC 360" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".env.sandbox")) {
    Write-Host "Erro: Arquivo .env.sandbox nao encontrado!" -ForegroundColor Red
    exit 1
}

$content = Get-Content ".env.sandbox"

function Check-Var {
    param($name, $badPattern)
    
    $line = $content | Where-Object { $_ -like "$name=*" } | Select-Object -First 1
    
    if ($line) {
        $value = $line.Split('=', 2)[1]
        if ($value -match $badPattern -or $value -eq "") {
            Write-Host "[X] $name - PRECISA CONFIGURAR" -ForegroundColor Red
            return $false
        } else {
            Write-Host "[OK] $name - Configurado" -ForegroundColor Green
            return $true
        }
    } else {
        Write-Host "[X] $name - NAO ENCONTRADO" -ForegroundColor Red
        return $false
    }
}

Write-Host "Verificando variaveis obrigatorias:" -ForegroundColor Yellow
Write-Host ""

$ok = $true

Write-Host "PayPal Sandbox:" -ForegroundColor Cyan
$ok = (Check-Var "PAYPAL_CLIENT_ID" "COLE_AQUI") -and $ok
$ok = (Check-Var "PAYPAL_SECRET" "COLE_AQUI") -and $ok
$ok = (Check-Var "PAYPAL_WEBHOOK_ID" "CRIAR_WEBHOOK|COLE_AQUI") -and $ok

Write-Host ""
Write-Host "Hugging Face:" -ForegroundColor Cyan
$ok = (Check-Var "HF_TOKEN" "COLE_AQUI") -and $ok

Write-Host ""
Write-Host "Seguranca:" -ForegroundColor Cyan
$ok = (Check-Var "DIOTEC360_SECRET_KEY" "GERE_UMA_CHAVE") -and $ok

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

if ($ok) {
    Write-Host "TODAS AS VARIAVEIS ESTAO CONFIGURADAS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximo passo: Copiar para .env" -ForegroundColor Cyan
    Write-Host "  Copy-Item .env.sandbox .env" -ForegroundColor Gray
} else {
    Write-Host "ALGUMAS VARIAVEIS PRECISAM SER CONFIGURADAS" -ForegroundColor Yellow
    Write-Host "Edite o arquivo .env.sandbox" -ForegroundColor Yellow
}

Write-Host ""
