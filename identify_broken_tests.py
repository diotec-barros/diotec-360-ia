"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Script para identificar testes quebrados no projeto Aethel
"""
import subprocess
import sys
from pathlib import Path

def check_test_file(test_file):
    """Verifica se um arquivo de teste pode ser executado"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Se retornou erro ou não coletou nenhum teste
        if result.returncode != 0:
            return False, result.stderr
        
        # Se coletou testes com sucesso
        if "test" in result.stdout.lower():
            return True, "OK"
        
        return False, "No tests collected"
        
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def main():
    # Lista todos os arquivos test_*.py
    test_files = list(Path(".").glob("test_*.py"))
    
    broken_tests = []
    working_tests = []
    
    print(f"🔍 Analisando {len(test_files)} arquivos de teste...\n")
    
    for test_file in sorted(test_files):
        print(f"Verificando {test_file.name}...", end=" ")
        is_working, message = check_test_file(test_file)
        
        if is_working:
            print("✅ OK")
            working_tests.append(test_file)
        else:
            print(f"❌ QUEBRADO ({message[:50]})")
            broken_tests.append((test_file, message))
    
    print(f"\n📊 RESUMO:")
    print(f"✅ Testes funcionais: {len(working_tests)}")
    print(f"❌ Testes quebrados: {len(broken_tests)}")
    
    if broken_tests:
        print(f"\n🗑️ TESTES QUEBRADOS PARA REMOVER:")
        for test_file, reason in broken_tests:
            print(f"  - {test_file.name}: {reason[:80]}")
        
        # Salvar lista de testes quebrados
        with open("broken_tests_list.txt", "w") as f:
            for test_file, reason in broken_tests:
                f.write(f"{test_file.name}\n")
        
        print(f"\n📝 Lista salva em: broken_tests_list.txt")

if __name__ == "__main__":
    main()
