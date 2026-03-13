# Quick HF Status Check
Write-Host "Verificando status do Sovereign Judge..." -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "https://diotec-360-diotec-360-ia-judge.hf.space/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "STATUS: ONLINE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resposta:" -ForegroundColor Yellow
    Write-Host $response.Content
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 503) {
        Write-Host "STATUS: Building (503 Service Unavailable)" -ForegroundColor Yellow
    } elseif ($statusCode -eq 502) {
        Write-Host "STATUS: Starting (502 Bad Gateway)" -ForegroundColor Yellow
    } else {
        Write-Host "STATUS: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Acompanhe em: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge" -ForegroundColor Gray
