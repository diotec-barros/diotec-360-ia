# DIOTEC 360 IA - Completar Deploy
# Desenvolvido por Kiro para Dionisio Sebastiao Barros

Write-Host "DIOTEC 360 IA - Completando Deploy" -ForegroundColor Cyan
Write-Host ""

# Verificar se o diretorio do Space existe
if (-not (Test-Path "diotec-360-ia-judge")) {
    Write-Host "Erro: Diretorio diotec-360-ia-judge nao encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\deploy_to_huggingface.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "PASSO 1: Fazer Login no Hugging Face" -ForegroundColor Yellow
Write-Host ""
Write-Host "Voce precisa de um token de acesso do Hugging Face." -ForegroundColor White
Write-Host ""
Write-Host "Para obter seu token:" -ForegroundColor Cyan
Write-Host "1. Acesse: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host "2. Clique em 'New token'" -ForegroundColor White
Write-Host "3. Nome: 'DIOTEC 360 Deploy'" -ForegroundColor White
Write-Host "4. Type: 'Write'" -ForegroundColor White
Write-Host "5. Copie o token gerado" -ForegroundColor White
Write-Host ""

# Fazer login usando hf (novo CLI)
Write-Host "Executando login..." -ForegroundColor Cyan
& "C:\Users\DIOTEC\.local\bin\hf.exe" auth login

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Falha no login!" -ForegroundColor Red
    Write-Host ""
    Write-Host "METODO ALTERNATIVO - Upload Manual:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge" -ForegroundColor White
    Write-Host "2. Clique em 'Files' -> 'Add file' -> 'Upload files'" -ForegroundColor White
    Write-Host "3. Arraste TODO o conteudo de: huggingface_deploy_package\" -ForegroundColor White
    Write-Host "4. Commit: 'Deploy DIOTEC 360 IA - Sovereign Judge'" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Login completo!" -ForegroundColor Green
Write-Host ""

Write-Host "PASSO 2: Fazer Push para o Space" -ForegroundColor Yellow
Write-Host ""

Set-Location diotec-360-ia-judge

# Tentar push novamente
git push

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Falha no push!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tentando com credenciais do hf..." -ForegroundColor Yellow
    
    # Configurar credential helper
    git config credential.helper store
    
    # Tentar push novamente
    git push
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "METODO ALTERNATIVO - Upload Manual:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge" -ForegroundColor White
        Write-Host "2. Clique em 'Files' -> 'Add file' -> 'Upload files'" -ForegroundColor White
        Write-Host "3. Arraste TODO o conteudo de: huggingface_deploy_package\" -ForegroundColor White
        Write-Host "4. Commit: 'Deploy DIOTEC 360 IA - Sovereign Judge'" -ForegroundColor White
        Write-Host ""
        Set-Location ..
        exit 1
    }
}

Set-Location ..

Write-Host ""
Write-Host "DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos Passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Aguarde o build completar (2-3 minutos)" -ForegroundColor White
Write-Host "   Status: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Quando o status ficar Running, teste:" -ForegroundColor White
Write-Host "   curl https://diotec-360-diotec-360-ia-judge.hf.space/" -ForegroundColor Gray
Write-Host ""
Write-Host "O MONOLITO ESTA VIVO!" -ForegroundColor Yellow
Write-Host "The Sovereign Judge is Online!" -ForegroundColor Cyan
Write-Host ""
