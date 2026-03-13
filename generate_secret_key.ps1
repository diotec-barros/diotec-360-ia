# ===========================================================================
# GERADOR DE SECRET_KEY PARA DIOTEC 360
# ===========================================================================
# Gera uma chave criptográfica forte e atualiza o arquivo .env
# Desenvolvido por: Kiro para Dionísio Sebastião Barros
# ===========================================================================

Write-Host "🔐 GERADOR DE SECRET_KEY - DIOTEC 360" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Gera uma chave hexadecimal de 64 caracteres (256 bits)
Write-Host "⚙️  Gerando chave criptográfica forte..." -ForegroundColor Yellow

$secretKey = -join ((48..57) + (65..70) + (97..102) | Get-Random -Count 64 | ForEach-Object {[char]$_})

Write-Host "✅ Chave gerada com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sua nova SECRET_KEY:" -ForegroundColor Cyan
Write-Host $secretKey -ForegroundColor White
Write-Host ""

# Pergunta se deseja atualizar o .env
$update = Read-Host "Deseja atualizar o arquivo .env automaticamente? (S/N)"

if ($update -eq "S" -or $update -eq "s") {
    if (Test-Path ".env") {
        # Lê o conteúdo do .env
        $envContent = Get-Content ".env" -Raw
        
        # Substitui a linha da SECRET_KEY
        $envContent = $envContent -replace 'DIOTEC360_SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI', "DIOTEC360_SECRET_KEY=$secretKey"
        
        # Salva o arquivo atualizado
        $envContent | Set-Content ".env" -NoNewline
        
        Write-Host "✅ Arquivo .env atualizado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔒 A chave foi inserida no arquivo .env" -ForegroundColor Green
    } else {
        Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor Red
        Write-Host "📋 Copie a chave acima manualmente" -ForegroundColor Yellow
    }
} else {
    Write-Host "📋 Copie a chave acima e cole manualmente no seu .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚠️  IMPORTANTE: Mantenha esta chave em segredo!" -ForegroundColor Red
Write-Host "   Nunca compartilhe ou commite no Git" -ForegroundColor Red
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🏛️  THE MONOLITH IS SECURE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
