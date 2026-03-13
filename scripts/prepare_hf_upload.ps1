# Prepara pacote para upload no Hugging Face
Write-Host "Preparando pacote para Hugging Face..." -ForegroundColor Cyan

# Criar pasta de upload
$uploadDir = "hf_upload_package"
if (Test-Path $uploadDir) {
    Remove-Item $uploadDir -Recurse -Force
}
New-Item -ItemType Directory -Path $uploadDir | Out-Null

# Copiar arquivos essenciais
Write-Host "Copiando arquivos..." -ForegroundColor Gray

Copy-Item "Dockerfile" "$uploadDir/"
Copy-Item "README_HF.md" "$uploadDir/README.md"
Copy-Item "api/requirements.txt" "$uploadDir/"

# Copiar pastas
Copy-Item "diotec360" "$uploadDir/" -Recurse
Copy-Item "api" "$uploadDir/" -Recurse

# Criar arquivo de instruções
@"
INSTRUÇÕES DE UPLOAD - HUGGING FACE
====================================

1. Acesse: https://huggingface.co/spaces
2. Clique "Create new Space"
3. Configure:
   - Nome: diotec360-api
 - SDK: Docker
   - Hardware: CPU basic (free)

4. Faça upload de TODOS os arquivos desta pasta

5. Configure Secrets (Settings > Variables):
   PAYPAL_CLIENT_ID=AZCY3ggrDLD9XNnvyVOGdU2ir7PsycmAyjro-0mFHv0XC5Fw2EAVrVrU1rqFDQZkWjYbAyksruNQGgAn
   PAYPAL_SECRET=EESM6eSh2vMjZUeNBCytDtbiIPAJan5hQgfwFb6rHZKvYAwta_SMO75MzNCrtHdf4SOP
   PAYPAL_WEBHOOK_ID=68N36636YR118321L
   PAYPAL_MODE=sandbox
   DIOTEC360_CORS_ORIGINS=*

6. Aguarde deploy automático (2-3 min)

PRONTO! Seu império está online! 🚀
"@ | Out-File "$uploadDir/LEIA_PRIMEIRO.txt" -Encoding UTF8

Write-Host ""
Write-Host "✅ Pacote pronto em: $uploadDir/" -ForegroundColor Green
Write-Host ""
Write-Host "Próximo passo:" -ForegroundColor Yellow
WritegroundColor White
Write-Host "2. Leia LEIA_PRIMEIRO.txt" -ForegroundColor White
Write-Host "3. Faça upload no Hugging Face" -ForegroundColor White
Write-Host ""
