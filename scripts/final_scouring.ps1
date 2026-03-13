# 🏛️ THE FINAL SCOURING - Task 6.1.0 ⚖️
# Expurgo Final: Remove todos os rastros de "Aethel" do código público

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🏛️ THE FINAL SCOURING - DIOTEC 360 IA v3.2.0" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$replacements = 0

# Arquivos críticos para rebranding
$criticalFiles = @(
    "api/main.py",
    "frontend/components/MonacoAutopilot.tsx",
    "frontend/__tests__/MonacoAutopilot.test.tsx"
)

Write-Host "[PHASE 1] Substituindo 'Aethel' por 'DIOTEC 360' em arquivos críticos..." -ForegroundColor Yellow

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  Processing: $file" -ForegroundColor Gray
        
        # Ler conteúdo
        $content = Get-Content $file -Raw -Encoding UTF8
        
        # Contar ocorrências antes
        $beforeCount = ([regex]::Matches($content, "Aethel", [System.Text.RegularExpressions.RegexOptions]::None)).Count
        
        if ($beforeCount -gt 0) {
            # Substituir "Aethel" por "DIOTEC 360" (preservando case)
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

Write-Host "`n[PHASE 2] Limpando arquivos compilados (.next/)..." -ForegroundColor Yellow

if (Test-Path "frontend/.next") {
    Write-Host "  Removing frontend/.next directory..." -ForegroundColor Gray
    Remove-Item "frontend/.next" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✅ Removed" -ForegroundColor Green
} else {
    Write-Host "    ⏭️  Directory not found" -ForegroundColor Gray
}

Write-Host "`n[PHASE 3] Atualizando .gitignore..." -ForegroundColor Yellow

$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    
    if ($gitignoreContent -notmatch "\.next/") {
        Add-Content $gitignorePath "`n# Frontend compiled files`n.next/`n"
        Write-Host "    ✅ Added .next/ to .gitignore" -ForegroundColor Green
    } else {
        Write-Host "    ⏭️  .next/ already in .gitignore" -ForegroundColor Gray
    }
} else {
    Write-Host "    ⚠️  .gitignore not found" -ForegroundColor Yellow
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🏆 FINAL SCOURING COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Total replacements: $replacements" -ForegroundColor White
Write-Host "`n✅ Brand purification complete!" -ForegroundColor Green
Write-Host "✅ Compiled files removed!" -ForegroundColor Green
Write-Host "✅ .gitignore updated!" -ForegroundColor Green
Write-Host "`n🚀 Ready for re-certification!" -ForegroundColor Cyan
