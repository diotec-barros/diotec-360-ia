# Script de migracao de imports: aethel -> diotec360
# Atualiza todos os arquivos .py no repositorio

$files = Get-ChildItem -Recurse -Filter *.py

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
    
    # Substituir imports: from aethel. -> from diotec360.
    $n = $n -replace '(^|\r?\n)(\s*from\s+)aethel(\.)', '${1}${2}diotec360$3'
    
    # Substituir imports: import aethel -> import diotec360
    $n = $n -replace '(^|\r?\n)(\s*import\s+)aethel(\b)', '${1}${2}diotec360$3'
    
    # Substituir strings de modulo em reloads
    $n = $n -replace "([`"'])aethel\.", '$1diotec360.'
    
    if ($n -ne $c) {
        Set-Content -LiteralPath $p -Value $n -NoNewline
        $modifiedFiles++
        Write-Host "OK: $($f.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Migracao completa!" -ForegroundColor Cyan
Write-Host "Arquivos processados: $totalFiles" -ForegroundColor White
Write-Host "Arquivos modificados: $modifiedFiles" -ForegroundColor Yellow
