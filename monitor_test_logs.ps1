# ===========================================================================
# MONITOR DE LOGS - TESTE PAYPAL SANDBOX
# ===========================================================================
# Monitora os logs do backend e frontend em tempo real
# ===========================================================================

$Host.UI.RawUI.WindowTitle = "DIOTEC 360 - Monitor de Logs"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  MONITOR DE LOGS - TESTE PAYPAL SANDBOX" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitorando processos..." -ForegroundColor Yellow
Write-Host ""
Write-Host "[Backend]  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "[Frontend] http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione CTRL+C para parar o monitoramento" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$lastBackendLines = 0
$lastFrontendLines = 0

while ($true) {
    Start-Sleep -Seconds 2
    
    # Limpa a tela a cada 20 iterações para não ficar muito poluído
    $iteration++
    if ($iteration -gt 20) {
        Clear-Host
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host "  MONITOR DE LOGS - ATUALIZACAO CONTINUA" -ForegroundColor Cyan
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host ""
        $iteration = 0
    }
    
    # Mostra timestamp
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Verificando logs..." -ForegroundColor Gray
    
    # Tenta ler logs do backend se existirem
    if (Test-Path "api\*.log") {
        $backendLogs = Get-Content "api\*.log" -Tail 5 -ErrorAction SilentlyContinue
        if ($backendLogs) {
            Write-Host ""
            Write-Host "[BACKEND] Ultimas 5 linhas:" -ForegroundColor Yellow
            $backendLogs | ForEach-Object {
                if ($_ -match "ERROR|error") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "WARNING|warning") {
                    Write-Host $_ -ForegroundColor Yellow
                } elseif ($_ -match "PayPal|PAYMENT|webhook") {
                    Write-Host $_ -ForegroundColor Cyan
                } else {
                    Write-Host $_ -ForegroundColor White
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
}
