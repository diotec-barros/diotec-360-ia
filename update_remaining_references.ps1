# Script para atualizar referencias restantes a "aethel"
# Atualiza arquivos .bat, .sh, .md e .env na raiz

$files = Get-ChildItem -Path "." -File -Include *.bat,*.sh,*.md,*.env,.env.* -Recurse -Depth 1 | Where-Object { 
    $_.FullName -notmatch '\\(\.git|node_modules|\.next|__pycache__|\.hypothesis|\.pytest_cache|\.kiro)\\' 
}

$totalFiles = 0
$modifiedFiles = 0

foreach ($f in $files) {
    $p = $f.FullName
    $c = Get-Content -LiteralPath $p -Raw -ErrorAction SilentlyContinue
    
    if (-not $c) {
        continue
    }
    
    $totalFiles++
    $n = $c
    
    # Variáveis de ambiente
    $n = $n -replace 'AETHEL_', 'DIOTEC360_'
    
    # Paths de diretório
    $n = $n -replace '\.aethel_', '.diotec360_'
    $n = $n -replace '/aethel/', '/diotec360/'
    
    # Topics P2P
    $n = $n -replace 'aethel/lattice', 'diotec360/lattice'
    
    # Nomes de serviço
    $n = $n -replace 'aethel-judge', 'diotec360-judge'
    $n = $n -replace 'aethel-lang', 'diotec360-lang'
    
    # URLs e domínios (manter alguns como referência externa)
    $n = $n -replace 'diotec-aethel-judge', 'diotec-diotec360-judge'
    $n = $n -replace 'aethel\.diotec360\.com', 'diotec360.diotec360.com'
    
    # Comentários e títulos
    $n = $n -replace 'REM Aethel', 'REM Diotec360'
    $n = $n -replace '# Aethel', '# Diotec360'
    $n = $n -replace 'AETHEL TRIANGLE', 'DIOTEC360 TRIANGLE'
    $n = $n -replace 'AETHEL REAL LATTICE', 'DIOTEC360 REAL LATTICE'
    $n = $n -replace 'Starting Aethel', 'Starting Diotec360'
    $n = $n -replace 'projeto "Aethel"', 'projeto "Diotec360"'
    
    # Scripts de teste
    $n = $n -replace 'teste_aethel\.bat', 'teste_diotec360.bat'
    
    if ($n -ne $c) {
        Set-Content -LiteralPath $p -Value $n -NoNewline
        $modifiedFiles++
        Write-Host "OK: $($f.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Atualizacao de referencias restantes completa!" -ForegroundColor Cyan
Write-Host "Arquivos processados: $totalFiles" -ForegroundColor White
Write-Host "Arquivos modificados: $modifiedFiles" -ForegroundColor Yellow
