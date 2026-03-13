# 🏛️ THE FINAL SCOURING - PHASE 2 ⚖️
# Expurgo dos arquivos restantes

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🏛️ FINAL SCOURING - PHASE 2" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$replacements = 0

# Arquivos restantes
$remainingFiles = @(
    "frontend/components/IdentityVault.tsx",
    "frontend/app/pricing/page.tsx",
    "api/autopilot.py",
    "frontend/app/explorer/page.tsx",
    "frontend/lib/agentNexus.ts"
)

Write-Host "[PHASE 2] Substituindo 'Aethel' nos arquivos restantes..." -ForegroundColor Yellow

foreach ($file in $remainingFiles) {
    if (Test-Path $file) {
        Write-Host "  Processing: $file" -ForegroundColor Gray
        
        # Ler conteúdo
        $content = Get-Content $file -Raw -Encoding UTF8
        
        # Contar ocorrências antes
        $beforeCount = ([regex]::Matches($content, "Aethel", [System.Text.RegularExpressions.RegexOptions]::None)).Count
        
        if ($beforeCount -gt 0) {
            # Substituir "Aethel" por "DIOTEC360"
            $content = $content -replace "Aethel", "DIOTEC360"
            $content = $content -replace "aethel", "diotec360"
            $content = $content -replace "AETHEL", "DIOTEC360"
            
            # Salvar
            [System.IO.File]::WriteAllText((Resolve-Path $file).Path, $content, [System.Text.Encoding]::UTF8)
            
            $replacements += $beforeCount
            Write-Host "    ✅ Replaced $beforeCount occurrence(s)" -ForegroundColor Green
        } else {
            Write-Host "    ⏭️  No occurrences found" -ForegroundColor Gray
        }
    } else {
        Write-Host "    ⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🏆 PHASE 2 COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Total replacements: $replacements" -ForegroundColor White
Write-Host "`n🚀 Re-running certification..." -ForegroundColor Cyan
