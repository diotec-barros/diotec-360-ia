# Script de limpeza final - Referencias restantes a "aethel"
# Atualiza arquivos de documentacao, scripts batch e configuracoes

Write-Host "=== LIMPEZA FINAL DE REFERENCIAS ===" -ForegroundColor Cyan
Write-Host ""

$patterns = @{
    # Variaveis de ambiente
    'AETHEL_' = 'DIOTEC360_'
    
    # Paths de diretorio
    '\.aethel_' = '.diotec360_'
    '/aethel/' = '/diotec360/'
    '\\aethel\\' = '\diotec360\'
    
    # URLs e espacos HF
    'diotec-aethel-judge' = 'diotec-diotec360-judge'
    'aethel-judge' = 'diotec360-judge'
    'aethel-studio' = 'diotec360-studio'
    'aethel-lang' = 'diotec360-lang'
    'aethel\.diotec360\.com' = 'diotec360.diotec360.com'
    
    # Titulos e textos
    'Aethel Performance' = 'Diotec360 Performance'
    'Aethel core' = 'Diotec360 core'
    'Aethel possui' = 'Diotec360 possui'
    'Aethel v' = 'Diotec360 v'
    'Aethel é' = 'Diotec360 é'
    'Aethel torna' = 'Diotec360 torna'
    'Core Aethel' = 'Core Diotec360'
    'Arquitetura Backend - Aethel' = 'Arquitetura Backend - Diotec360'
    'APLICAÇÃO AETHEL' = 'APLICAÇÃO DIOTEC360'
    'AETHEL TRIANGLE' = 'DIOTEC360 TRIANGLE'
    'AETHEL REAL LATTICE' = 'DIOTEC360 REAL LATTICE'
    'AETHEL LATTICE' = 'DIOTEC360 LATTICE'
    'AETHEL PERSISTENCE' = 'DIOTEC360 PERSISTENCE'
    
    # Imports e modulos
    'from aethel_generator' = 'from diotec360_generator'
    'aethel_generator\.py' = 'diotec360_generator.py'
    
    # Comentarios em scripts
    'Aethel API Server' = 'Diotec360 API Server'
    'Aethel Node' = 'Diotec360 Node'
}

$extensions = @('*.md', '*.txt', '*.bat', '*.sh', '*.env*', '*.json', '*.yaml', '*.yml')
$excludeDirs = @('.git', 'node_modules', '.next', '__pycache__', '.hypothesis', '.pytest_cache', '.kiro', 'logs', 'output')

$totalFiles = 0
$modifiedFiles = 0

foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path . -Filter $ext -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { 
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -like "*\$dir\*") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    
    foreach ($f in $files) {
        $totalFiles++
        $content = Get-Content -LiteralPath $f.FullName -Raw -ErrorAction SilentlyContinue
        
        if (-not $content) { continue }
        
        $modified = $false
        $newContent = $content
        
        foreach ($pattern in $patterns.GetEnumerator()) {
            if ($newContent -match [regex]::Escape($pattern.Key)) {
                $newContent = $newContent -replace [regex]::Escape($pattern.Key), $pattern.Value
                $modified = $true
            }
        }
        
        if ($modified) {
            Set-Content -LiteralPath $f.FullName -Value $newContent -NoNewline
            $modifiedFiles++
            Write-Host "OK: $($f.Name)" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Limpeza completa!" -ForegroundColor Cyan
Write-Host "Arquivos processados: $totalFiles" -ForegroundColor White
Write-Host "Arquivos modificados: $modifiedFiles" -ForegroundColor Yellow
