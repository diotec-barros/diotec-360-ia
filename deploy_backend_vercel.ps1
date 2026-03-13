# Deploy Backend para Vercel - DIOTEC 360
Write-Host "=== Deploy Backend API para Vercel ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Iniciando deploy do backend..." -ForegroundColor Yellow
Write-Host ""

# Criar arquivo de configuração do Vercel
$vercelConfig = @"
{
  "name": "diotec360-api",
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
"@

Write-Host "Configuracao do projeto:" -ForegroundColor White
Write-Host "  Nome: diotec360-api" -ForegroundColor Gray
Write-Host "  Framework: Python (FastAPI)" -ForegroundColor Gray
Write-Host "  Dominio: api.diotec360.com" -ForegroundColor Gray
Write-Host ""

Write-Host "Execute o seguinte comando manualmente:" -ForegroundColor Yellow
Write-Host ""
Write-Host "vercel --prod" -ForegroundColor White
Write-Host ""
Write-Host "Quando solicitado, responda:" -ForegroundColor Yellow
Write-Host "  Set up and deploy? YES" -ForegroundColor Gray
Write-Host "  Which scope? diotec-barros" -ForegroundColor Gray
Write-Host "  Link to existing project? NO" -ForegroundColor Gray
Write-Host "  Project name? diotec360-api" -ForegroundColor Gray
Write-Host "  Directory? . (raiz)" -ForegroundColor Gray
Write-Host "  Override settings? NO" -ForegroundColor Gray
Write-Host ""
Write-Host "Apos o deploy, adicione o dominio:" -ForegroundColor Yellow
Write-Host "  vercel domains add api.diotec360.com" -ForegroundColor White
Write-Host ""
