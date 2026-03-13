# Script para atualizar todas as referências a "Aethel" nos testes
# Migração: aethel -> diotec360

$testFiles = Get-ChildItem -Path . -Filter "test_*.py"

foreach ($file in $testFiles) {
    Write-Host "Processando: $($file.Name)"
    
    $content = Get-Content -Path $file.FullName -Raw
    
    # Substituições gerais
    $content = $content -replace '\bAethel\b', 'Diotec360'
    $content = $content -replace '\baethel\b', 'diotec360'
    $content = $content -replace 'AETHEL', 'DIOTEC360'
    
    # Imports específicos
    $content = $content -replace 'from aethel_kernel import', 'from diotec360_kernel import'
    $content = $content -replace 'from aethel_weaver import', 'from diotec360_weaver import'
    
    # Classes e funções
    $content = $content -replace 'AethelKernel', 'Diotec360Kernel'
    $content = $content -replace 'AethelWeaver', 'Diotec360Weaver'
    $content = $content -replace 'AethelParser', 'Diotec360Parser'
    $content = $content -replace 'AethelJudge', 'Diotec360Judge'
    $content = $content -replace 'AethelCrypt', 'Diotec360Crypt'
    $content = $content -replace 'AethelVault', 'Diotec360Vault'
    $content = $content -replace 'AethelWasmCompiler', 'Diotec360WasmCompiler'
    $content = $content -replace 'AethelWasmRuntime', 'Diotec360WasmRuntime'
    $content = $content -replace 'AethelDistributedVault', 'Diotec360DistributedVault'
    $content = $content -replace 'AethelStateManager', 'Diotec360StateManager'
    
    # Paths
    $content = $content -replace '\.aethel_vault', '.diotec360_vault'
    $content = $content -replace 'aethel/examples/', 'diotec360/examples/'
    
    # URLs
    $content = $content -replace 'diotec-aethel-judge', 'diotec360-judge'
    
    # IDs e prefixos
    $content = $content -replace 'AETHEL-CERT-', 'DIOTEC360-CERT-'
    $content = $content -replace 'aethel-pilot-', 'diotec360-pilot-'
    
    # Variáveis de ambiente
    $content = $content -replace 'AETHEL_OFFLINE', 'DIOTEC360_OFFLINE'
    $content = $content -replace 'AETHEL_TEST_MODE', 'DIOTEC360_TEST_MODE'
    
    # Salvar arquivo
    Set-Content -Path $file.FullName -Value $content -NoNewline
}

Write-Host "`n✅ Atualização completa!"
Write-Host "Arquivos processados: $($testFiles.Count)"
