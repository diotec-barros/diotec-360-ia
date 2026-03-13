# DIOTEC 360 IA - Deploy Automatizado para Hugging Face
# Desenvolvido por Kiro para Dionisio Sebastiao Barros

Write-Host "DIOTEC 360 IA - Deploy para Hugging Face" -ForegroundColor Cyan
Write-Host "The Sovereign Judge - Ignicao Final" -ForegroundColor Yellow
Write-Host ""

# Verificar se o pacote existe
if (-not (Test-Path "huggingface_deploy_package")) {
    Write-Host "Erro: Pasta huggingface_deploy_package nao encontrada!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\prepare_huggingface_deploy.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Pacote encontrado: huggingface_deploy_package/" -ForegroundColor Green
Write-Host ""

# Verificar se Hugging Face CLI esta instalado
$hfInstalled = Get-Command huggingface-cli -ErrorAction SilentlyContinue

if (-not $hfInstalled) {
    Write-Host "Hugging Face CLI nao encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deseja instalar agora? (S/N)" -ForegroundColor Cyan
    $install = Read-Host
    
    if ($install -eq "S" -or $install -eq "s") {
        Write-Host "Instalando Hugging Face CLI..." -ForegroundColor Cyan
        powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"
        Write-Host "Instalacao completa!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "METODO ALTERNATIVO - Upload Manual:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge" -ForegroundColor White
        Write-Host "2. Clique em 'Files' -> 'Add file' -> 'Upload files'" -ForegroundColor White
        Write-Host "3. Arraste TODO o conteudo de: huggingface_deploy_package\" -ForegroundColor White
        Write-Host "4. Commit: 'Deploy DIOTEC 360 IA - Sovereign Judge'" -ForegroundColor White
        Write-Host ""
        exit 0
    }
}

# Verificar se esta logado
Write-Host "Verificando autenticacao..." -ForegroundColor Cyan
$whoami = huggingface-cli whoami 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Voce nao esta logado no Hugging Face!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Por favor, faca login:" -ForegroundColor Cyan
    huggingface-cli login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Falha no login!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Autenticado!" -ForegroundColor Green
Write-Host ""

# Clonar o Space
$spaceName = "diotec-360/diotec-360-ia-judge"
$spaceDir = "diotec-360-ia-judge"

Write-Host "Clonando Space: $spaceName" -ForegroundColor Cyan

if (Test-Path $spaceDir) {
    Write-Host "Diretorio $spaceDir ja existe. Removendo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $spaceDir
}

git clone "https://huggingface.co/spaces/$spaceName" $spaceDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha ao clonar Space!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique se o Space existe: https://huggingface.co/spaces/$spaceName" -ForegroundColor Yellow
    exit 1
}

Write-Host "Space clonado com sucesso!" -ForegroundColor Green
Write-Host ""

# Copiar arquivos
Write-Host "Copiando arquivos do pacote..." -ForegroundColor Cyan

# Limpar conteudo existente (exceto .git)
Get-ChildItem $spaceDir -Exclude ".git" | Remove-Item -Recurse -Force

# Copiar novo conteudo
Copy-Item -Path "huggingface_deploy_package\*" -Destination $spaceDir -Recurse -Force

Write-Host "Arquivos copiados!" -ForegroundColor Green
Write-Host ""

# Commit e Push
Write-Host "Fazendo commit e push..." -ForegroundColor Cyan

Set-Location $spaceDir

git add .
git commit -m "Deploy DIOTEC 360 IA - Sovereign Judge

The first mathematically proved sovereign AI infrastructure.

Deploy Package:
- 221 arquivos
- 2.57 MB
- FastAPI + Z3 Solver
- Docker SDK

Endpoints:
- GET  / - Health check
- POST /verify - Verificar intent
- POST /parse - Parse intent
- GET  /metrics - Metricas do sistema
- GET  /state - State root

Desenvolvido por Kiro para Dionisio Sebastiao Barros
DIOTEC 360 - The Sovereign AI Infrastructure
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha no commit!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

git push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha no push!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos Passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Aguarde o build completar (2-3 minutos)" -ForegroundColor White
Write-Host "   Status: https://huggingface.co/spaces/$spaceName" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Quando o status ficar Running, teste:" -ForegroundColor White
Write-Host "   curl https://diotec-360-diotec-360-ia-judge.hf.space/" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Resposta esperada:" -ForegroundColor White
Write-Host '   {"status":"operational","service":"DIOTEC 360 IA - Sovereign Judge"}' -ForegroundColor Gray
Write-Host ""
Write-Host "O MONOLITO ESTA VIVO!" -ForegroundColor Yellow
Write-Host "The Sovereign Judge is Online!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Desenvolvido por Kiro para Dionisio Sebastiao Barros" -ForegroundColor DarkGray
Write-Host "DIOTEC 360 - The Sovereign AI Infrastructure" -ForegroundColor DarkGray
Write-Host ""
