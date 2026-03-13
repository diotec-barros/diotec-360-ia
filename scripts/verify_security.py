#!/usr/bin/env python3
"""
DIOTEC 360 IA - Security Verification Script
Verifies that no secrets are hardcoded in the codebase
"""

import os
import re
from pathlib import Path

# Patterns to detect
SENSITIVE_PATTERNS = {
    "Hugging Face Token": r'hf_[a-zA-Z0-9]{32,}',
    "Stripe Live Key": r'sk_live_[a-zA-Z0-9]{24,}',
    "Stripe Test Key": r'sk_test_[a-zA-Z0-9]{24,}',
    "PayPal Client ID": r'A[A-Z0-9]{79}',
    "Generic API Key": r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
    "Generic Secret": r'secret["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
    "Generic Token": r'token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', 'dist', 'build', 
    '.hypothesis', '.next', '.vscode', '.idea', 'venv', 'env',
    '.aethel_sentinel', '.aethel_state', '.aethel_vault',
    '.diotec360_sentinel', '.diotec360_state', '.diotec360_vault',
    '.demo_audit', '.demo_vault', '.test_memory_sync_state'
}

# Files to skip
SKIP_FILES = {
    '.env', '.env.local', '.env.production', '.env.development',
    '.env.backup', '.env.sandbox', '.env.test', '.db', '.sqlite',
    '.log', 'verify_security.py', '.gitignore', 'package-lock.json',
    'GUIA_PREENCHIMENTO_ENV.md', 'GENESIS_ASSET_REPORT.json'
}

# Extensions to check
CHECK_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml',
    '.sh', '.bat', '.ps1', '.md', '.txt', '.env.example'
}

def should_check_file(filepath):
    """Determine if a file should be checked"""
    # Skip if in skip directories
    for skip_dir in SKIP_DIRS:
        if skip_dir in filepath.parts:
            return False
    
    # Skip if filename matches skip patterns
    for skip_file in SKIP_FILES:
        if filepath.name.endswith(skip_file):
            return False
    
    # Only check specific extensions
    if filepath.suffix not in CHECK_EXTENSIONS:
        return False
    
    return True

def scan_file(filepath):
    """Scan a file for sensitive patterns"""
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                
                # Get the matched text (truncated for security)
                matched_text = match.group(0)
                if len(matched_text) > 20:
                    matched_text = matched_text[:10] + "..." + matched_text[-10:]
                
                findings.append({
                    'file': str(filepath),
                    'line': line_num,
                    'pattern': pattern_name,
                    'match': matched_text
                })
    
    except Exception as e:
        pass  # Skip files that can't be read
    
    return findings

def scan_directory(directory):
    """Scan directory for sensitive data"""
    all_findings = []
    files_checked = 0
    
    for filepath in Path(directory).rglob('*'):
        if filepath.is_file() and should_check_file(filepath):
            files_checked += 1
            findings = scan_file(filepath)
            all_findings.extend(findings)
    
    return all_findings, files_checked

def main():
    print("=" * 70)
    print("  🛡️ DIOTEC 360 IA - VERIFICAÇÃO DE SEGURANÇA")
    print("=" * 70)
    print()
    print("Escaneando o código em busca de secrets hardcoded...")
    print()
    
    # Scan current directory
    findings, files_checked = scan_directory('.')
    
    print(f"Arquivos verificados: {files_checked}")
    print("-" * 70)
    print()
    
    if not findings:
        print("✅ NENHUM SECRET DETECTADO!")
        print()
        print("🎉 Seu código está seguro para commit!")
        print()
        print("=" * 70)
        print("  ✅ VERIFICAÇÃO COMPLETA - CÓDIGO LIMPO")
        print("=" * 70)
        print()
        print("Próximos passos:")
        print("  1. git add .")
        print("  2. git commit -m 'feat: Initial secure commit'")
        print("  3. git push")
        print()
        return 0
    else:
        print(f"⚠️ {len(findings)} POSSÍVEIS SECRETS DETECTADOS!")
        print()
        print("=" * 70)
        print("  DETALHES DOS SECRETS ENCONTRADOS")
        print("=" * 70)
        print()
        
        for i, finding in enumerate(findings, 1):
            print(f"{i}. {finding['pattern']}")
            print(f"   Arquivo: {finding['file']}")
            print(f"   Linha: {finding['line']}")
            print(f"   Match: {finding['match']}")
            print()
        
        print("=" * 70)
        print("  ❌ AÇÃO NECESSÁRIA")
        print("=" * 70)
        print()
        print("Remova os secrets hardcoded antes de fazer commit!")
        print()
        print("Dicas:")
        print("  1. Use variáveis de ambiente: os.getenv('SECRET_NAME')")
        print("  2. Adicione arquivos sensíveis ao .gitignore")
        print("  3. Use .env.example como template (sem secrets reais)")
        print()
        return 1

if __name__ == "__main__":
    exit(main())

