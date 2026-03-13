# Fix Hugging Face Deploy - Atualizar paths .aethel_ para .diotec360_
# Desenvolvido por Kiro para Dionisio Sebastiao Barros

Write-Host "Corrigindo referencias .aethel_ no pacote HF..." -ForegroundColor Cyan
Write-Host ""

$files = @(
    "huggingface_deploy_package/diotec360/core/state.py",
    "huggingface_deploy_package/diotec360/core/sentinel_monitor.py",
    "huggingface_deploy_package/diotec360/core/persistence.py",
    "huggingface_deploy_package/diotec360/core/memory.py",
    "huggingface_deploy_package/diotec360/core/kernel.py",
    "huggingface_deploy_package/diotec360/core/judge.py",
    "huggingface_deploy_package/diotec360/core/integrity_panic.py"
)

$replacements = @{
    ".aethel_vault" = ".diotec360_vault"
    ".aethel_state" = ".diotec360_state"
    ".aethel_moe" = ".diotec360_moe"
    ".aethel_sentinel" = ".diotec360_sentinel"
    ".aethel_vigilance" = ".diotec360_vigilance"
    ".aethel_lattice" = ".diotec360_lattice"
}

$totalChanges = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $originalContent = $content
        
        foreach ($old in $replacements.Keys) {
            $new = $replacements[$old]
            $content = $content -replace [regex]::Escape($old), $new
        }
        
        if ($content -ne $originalContent) {
            Set-Content -Path $file -Value $content -NoNewline
            Write-Host "  Atualizado: $file" -ForegroundColor Green
            $totalChanges++
        }
    }
}

Write-Host ""
Write-Host "Total de arquivos atualizados: $totalChanges" -ForegroundColor Yellow
Write-Host ""
Write-Host "Concluido!" -ForegroundColor Green
