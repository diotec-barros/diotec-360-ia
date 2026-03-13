# Fix UTF-8 Encoding for Hugging Face Deployment
Write-Host "=== Fixing UTF-8 Encoding ===" -ForegroundColor Cyan

$sourceFile = "diotec360\core\judge.py"
$destFile = "huggingface_deploy_package\diotec360\core\judge.py"

Write-Host "Copying: $sourceFile -> $destFile" -ForegroundColor Yellow

# Read and write with UTF-8 (no BOM)
$content = Get-Content -Path $sourceFile -Encoding UTF8 -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($destFile, $content, $utf8NoBom)

Write-Host "Done!" -ForegroundColor Green
