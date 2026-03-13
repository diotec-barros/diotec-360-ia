# Setup Vercel Domains - DIOTEC 360
Write-Host "=== DIOTEC 360 - Configuracao de Subdominios Vercel ===" -ForegroundColor Cyan
Write-Host ""

# Verificar Vercel CLI
Write-Host "Verificando Vercel CLI..." -ForegroundColor Yellow
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue

if (-not $vercelInstalled) 
{
    Write-Host "Vercel CLI nao encontrado. Instalando..." -ForegroundColor Yellow
    npm install -g vercel
    
    if ($LASTEXITCODE -ne 0) 
    {
        Write-Host "Falha ao instalar Vercel CLI" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Vercel CLI instalado!" -ForegroundColor Green
} 
else 
{
    Write-Host "Vercel CLI encontrado" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Passo 1: Login no Vercel ===" -ForegroundColor Cyan
Write-Host "Abrindo navegador para autenticacao..." -ForegroundColor Yellow
vercel login

if ($LASTEXITCODE -ne 0) 
{
    Write-Host "Falha no login" -ForegroundColor Red
    exit 1
}

Write-Host "Login realizado!" -ForegroundColor Green
Write-Host ""

# Verificar DNS
Write-Host "=== Passo 2: Verificar DNS ===" -ForegroundColor Cyan
Write-Host ""

$domains = @("api.diotec360.com", "app.diotec360.com")

foreach ($domain in $domains) 
{
    Write-Host "Verificando DNS para $domain..." -ForegroundColor Yellow
    
    try 
    {
        $dnsResult = Resolve-DnsName -Name $domain -Type CNAME -ErrorAction SilentlyContinue
        
        if ($dnsResult) 
        {
            Write-Host "DNS configurado: $domain" -ForegroundColor Green
        } 
        else 
        {
            Write-Host "DNS nao encontrado para $domain" -ForegroundColor Yellow
            Write-Host "Configure o CNAME: $domain -> cname.vercel-dns.com" -ForegroundColor Yellow
        }
    } 
    catch 
    {
        Write-Host "Nao foi possivel verificar DNS para $domain" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

Write-Host "=== Passo 3: Comandos de Deploy ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API (api.diotec360.com):" -ForegroundColor Yellow
Write-Host "  vercel --prod" -ForegroundColor White
Write-Host "  vercel domains add api.diotec360.com" -ForegroundColor White
Write-Host ""
Write-Host "Frontend App (app.diotec360.com):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  vercel --prod" -ForegroundColor White
Write-Host "  vercel domains add app.diotec360.com" -ForegroundColor White
Write-Host ""

Write-Host "=== Resumo ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dominios:" -ForegroundColor White
Write-Host "  api.diotec360.com  -> Backend API" -ForegroundColor Gray
Write-Host "  app.diotec360.com  -> Frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentacao: VERCEL_SUBDOMINIOS_GUIA.md" -ForegroundColor Yellow
Write-Host "DNS Config: DNS_CONFIGURATION.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Concluido ===" -ForegroundColor Green
