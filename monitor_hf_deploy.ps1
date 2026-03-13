# DIOTEC 360 IA - Monitor de Deploy Hugging Face
# Desenvolvido por Kiro para Dionisio Sebastiao Barros

Write-Host "DIOTEC 360 IA - Monitor de Deploy" -ForegroundColor Cyan
Write-Host ""

$spaceUrl = "https://diotec-360-diotec-360-ia-judge.hf.space"
$spaceWebUrl = "https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge"

Write-Host "Space URL: $spaceWebUrl" -ForegroundColor Yellow
Write-Host "API URL: $spaceUrl" -ForegroundColor Yellow
Write-Host ""

Write-Host "Testando conectividade..." -ForegroundColor Cyan
Write-Host ""

$maxAttempts = 20
$attempt = 0
$success = $false

while ($attempt -lt $maxAttempts -and -not $success) {
    $attempt++
    
    Write-Host "[$attempt/$maxAttempts] Tentando conectar..." -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $spaceUrl -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "SUCESSO! API esta online!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Resposta:" -ForegroundColor Cyan
            Write-Host $response.Content -ForegroundColor White
            Write-Host ""
            $success = $true
        }
    }
    catch {
        $errorMsg = $_.Exception.Message
        
        if ($errorMsg -like "*503*") {
            Write-Host "  Status: Building (Container sendo construido)..." -ForegroundColor Yellow
        }
        elseif ($errorMsg -like "*502*") {
            Write-Host "  Status: Starting (Iniciando container)..." -ForegroundColor Yellow
        }
        elseif ($errorMsg -like "*404*") {
            Write-Host "  Status: Not Found (Verificar configuracao)..." -ForegroundColor Red
        }
        else {
            Write-Host "  Status: Aguardando..." -ForegroundColor Gray
        }
        
        if ($attempt -lt $maxAttempts) {
            Start-Sleep -Seconds 10
        }
    }
}

Write-Host ""

if ($success) {
    Write-Host "O MONOLITO ESTA VIVO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Endpoints disponiveis:" -ForegroundColor Cyan
    Write-Host "  GET  $spaceUrl/" -ForegroundColor White
    Write-Host "  POST $spaceUrl/verify" -ForegroundColor White
    Write-Host "  POST $spaceUrl/parse" -ForegroundColor White
    Write-Host "  GET  $spaceUrl/metrics" -ForegroundColor White
    Write-Host "  GET  $spaceUrl/state" -ForegroundColor White
    Write-Host ""
    Write-Host "Teste com curl:" -ForegroundColor Cyan
    Write-Host "  curl $spaceUrl/" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "Build ainda em progresso..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Acompanhe o status em:" -ForegroundColor Cyan
    Write-Host "  $spaceWebUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "O build pode levar 2-5 minutos." -ForegroundColor Gray
    Write-Host "Execute este script novamente para verificar." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Desenvolvido por Kiro para Dionisio Sebastiao Barros" -ForegroundColor DarkGray
Write-Host "DIOTEC 360 - The Sovereign AI Infrastructure" -ForegroundColor DarkGray
Write-Host ""
