# Script para atualizar referencias a "aethel" na documentacao
# Substitui imports, paths e referencias textuais

$files = Get-ChildItem -Path "docs" -Recurse -Filter *.md

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
    
    # Substituir imports Python: from aethel. -> from diotec360.
    $n = $n -replace 'from aethel\.', 'from diotec360.'
    
    # Substituir paths de diretorio: .aethel_ -> .diotec360_
    $n = $n -replace '\.aethel_', '.diotec360_'
    
    # Substituir paths: /aethel/ -> /diotec360/
    $n = $n -replace '/aethel/', '/diotec360/'
    
    # Substituir paths Windows: \aethel\ -> \diotec360\
    $n = $n -replace '\\aethel\\', '\diotec360\'
    
    # Substituir referencias de componente: aethel/core -> diotec360/core
    $n = $n -replace '`aethel/', '`diotec360/'
    
    # Substituir "Aethel Team" -> "Diotec360 Team"
    $n = $n -replace 'Aethel ([A-Z][a-z]+ )?Team', 'Diotec360 $1Team'
    
    # Substituir "Aethel system" -> "Diotec360 system"
    $n = $n -replace 'Aethel system', 'Diotec360 system'
    
    # Substituir "the Aethel" -> "the Diotec360"
    $n = $n -replace 'the Aethel([^-])', 'the Diotec360$1'
    
    if ($n -ne $c) {
        Set-Content -LiteralPath $p -Value $n -NoNewline
        $modifiedFiles++
        Write-Host "OK: $($f.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Atualizacao de documentacao completa!" -ForegroundColor Cyan
Write-Host "Arquivos processados: $totalFiles" -ForegroundColor White
Write-Host "Arquivos modificados: $modifiedFiles" -ForegroundColor Yellow
