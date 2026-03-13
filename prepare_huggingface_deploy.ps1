# Script para preparar deploy no Hugging Face Space
# DIOTEC 360 IA - Sovereign Judge

Write-Host "======================================================================"
Write-Host "DIOTEC 360 IA - Preparação para Deploy no Hugging Face"
Write-Host "======================================================================"

# Criar diretório de deploy limpo
$deployDir = "huggingface_deploy_package"

if (Test-Path $deployDir) {
    Write-Host "`nRemovendo diretório anterior..."
    Remove-Item -Recurse -Force $deployDir
}

Write-Host "`nCriando estrutura de deploy..."
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copiar arquivos de configuração
Write-Host "`nCopiando arquivos de configuração..."
Copy-Item "huggingface_deploy/README.md" "$deployDir/"
Copy-Item "huggingface_deploy/requirements.txt" "$deployDir/"
Copy-Item "huggingface_deploy/Dockerfile" "$deployDir/"
Copy-Item "huggingface_deploy/.dockerignore" "$deployDir/"
Copy-Item "huggingface_deploy/.env.production" "$deployDir/.env"

# Copiar código principal
Write-Host "`nCopiando código DIOTEC 360..."
Copy-Item -Recurse "diotec360" "$deployDir/"

# Copiar API
Write-Host "`nCopiando API..."
Copy-Item -Recurse "api" "$deployDir/"

# Criar diretórios necessários
Write-Host "`nCriando diretórios de dados..."
New-Item -ItemType Directory -Path "$deployDir/.diotec360_vault" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir/.diotec360_state" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir/.diotec360_audit" -Force | Out-Null

# Criar arquivo .gitkeep para manter diretórios vazios
"" | Out-File "$deployDir/.diotec360_vault/.gitkeep"
"" | Out-File "$deployDir/.diotec360_state/.gitkeep"
"" | Out-File "$deployDir/.diotec360_audit/.gitkeep"

# Limpar arquivos desnecessários
Write-Host "`nLimpando arquivos desnecessários..."
Get-ChildItem -Path $deployDir -Recurse -Include "__pycache__","*.pyc","*.pyo","*.log","*.db" | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

# Criar arquivo de instruções
Write-Host "`nCriando instruções de deploy..."
Copy-Item "huggingface_deploy/DEPLOY_INSTRUCTIONS.md" "$deployDir/"

# Estatísticas
Write-Host "`nEstatísticas do pacote:"
$fileCount = (Get-ChildItem -Path $deployDir -Recurse -File).Count
$totalSize = (Get-ChildItem -Path $deployDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "   Arquivos: $fileCount"
Write-Host "   Tamanho total: $([math]::Round($totalSize, 2)) MB"

# Verificar arquivos críticos
Write-Host "`nVerificando arquivos críticos..."
$critical = @(
    "README.md",
    "requirements.txt",
    "Dockerfile",
    "api/main.py",
    "diotec360/core/parser.py",
    "diotec360/core/judge.py"
)

$allOk = $true
foreach ($f in $critical) {
    $fullPath = Join-Path $deployDir $f
    if (Test-Path $fullPath) {
        Write-Host "   OK: $f"
    } else {
        Write-Host "   FALTANDO: $f" -ForegroundColor Red
        $allOk = $false
    }
}

if ($allOk) {
    Write-Host "`nPacote de deploy preparado com sucesso!" -ForegroundColor Green
    Write-Host "`nLocalização: $deployDir"
    Write-Host "`nPróximos passos:"
    Write-Host "   1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge"
    Write-Host "   2. Clique em 'Files' -> 'Add file' -> 'Upload files'"
    Write-Host "   3. Arraste todo o conteúdo de '$deployDir'"
    Write-Host "   4. Clique em 'Commit changes to main'"
    Write-Host "   5. Aguarde o build completar (status verde)"
    Write-Host "`nO Sovereign Judge estará online em:"
    Write-Host "   https://diotec-360-diotec-360-ia-judge.hf.space"
} else {
    Write-Host "`nERRO: Alguns arquivos críticos estão faltando!" -ForegroundColor Red
    Write-Host "   Verifique a estrutura do projeto antes de fazer deploy."
}

Write-Host "`n======================================================================"
