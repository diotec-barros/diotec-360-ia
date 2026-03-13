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

import os
from datetime import datetime
from diotec360.core.parser import AethelParser
from diotec360.core.bridge import AethelBridge
from diotec360.core.judge import AethelJudge


class AethelGenerator:
    """
    Orquestrador principal que conecta Parser -> Bridge -> AI -> Artifact
    """
    
    def __init__(self, ai_provider="anthropic", enable_verification=True):
        self.parser = AethelParser()
        self.ai_provider = ai_provider
        self.enable_verification = enable_verification
        self._validate_api_keys()
    
    def _validate_api_keys(self):
        """Verifica se as chaves de API estão configuradas"""
        if self.ai_provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                print("⚠️  ANTHROPIC_API_KEY não encontrada. Configure para usar geração real.")
        elif self.ai_provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("⚠️  OPENAI_API_KEY não encontrada. Configure para usar geração real.")
        elif self.ai_provider == "ollama":
            self.api_key = None  # Ollama não precisa de chave
            print("🦙 Usando Ollama local")
    
    def compile(self, aethel_code, intent_name=None, output_file=None):
        """
        Pipeline completo: Aethel -> AST -> Verification -> Prompt -> AI -> Rust
        """
        print("🔍 [1/6] Parsing código Aethel...")
        ast = self.parser.parse(aethel_code)
        
        # Se não especificou intent, usa o primeiro
        if intent_name is None:
            intent_name = list(ast.keys())[0]
        
        # VERIFICAÇÃO FORMAL ANTES DA GERAÇÃO
        verification_result = None
        if self.enable_verification:
            print(f"⚖️  [2/6] Verificação formal da lógica...")
            judge = AethelJudge(ast)
            verification_result = judge.verify_logic(intent_name)
            
            if verification_result['status'] == 'FAILED':
                print("\n❌ COMPILAÇÃO ABORTADA!")
                print("O Juiz detectou falhas lógicas nas constraints.")
                report = judge.generate_proof_report(intent_name, verification_result)
                print(report)
                
                return {
                    "status": "FAILED",
                    "ast": ast,
                    "verification": verification_result,
                    "report": report
                }
            else:
                print(f"✅ Verificação formal: {verification_result['message']}")
        
        print(f"🌉 [3/6] Construindo ponte para intent '{intent_name}'...")
        bridge = AethelBridge(ast)
        prompt = bridge.generate_generation_prompt(intent_name)
        
        print("🤖 [4/6] Enviando para gerador de IA...")
        generated_code = self._call_ai(prompt)
        
        print("📦 [5/6] Empacotando artefato final...")
        artifact = bridge.build_final_artifact(generated_code, intent_name)
        artifact = artifact.replace("{timestamp}", datetime.now().isoformat())
        
        print("💾 [6/6] Salvando código gerado...")
        if output_file:
            with open(output_file, 'w') as f:
                f.write(artifact)
            print(f"✅ Código salvo em: {output_file}")
        
        # Gerar relatório de verificação se habilitado
        report = None
        if self.enable_verification and verification_result:
            report = judge.generate_proof_report(intent_name, verification_result)
        
        return {
            "status": "SUCCESS",
            "ast": ast,
            "verification": verification_result,
            "prompt": prompt,
            "generated_code": generated_code,
            "artifact": artifact,
            "report": report
        }
    
    def _call_ai(self, prompt):
        """
        Chama a API de IA escolhida
        """
        if not self.api_key and self.ai_provider != "ollama":
            print("⚠️  Modo simulação (sem API key)")
            return self._simulate_generation()
        
        if self.ai_provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.ai_provider == "openai":
            return self._call_openai(prompt)
        elif self.ai_provider == "ollama":
            return self._call_ollama(prompt)
    
    def _call_anthropic(self, prompt):
        """Chama Claude via Anthropic API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except ImportError:
            print("⚠️  Biblioteca 'anthropic' não instalada. Execute: pip install anthropic")
            return self._simulate_generation()
        except Exception as e:
            print(f"❌ Erro ao chamar Anthropic: {e}")
            return self._simulate_generation()
    
    def _call_openai(self, prompt):
        """Chama GPT via OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Rust code generator."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
        except ImportError:
            print("⚠️  Biblioteca 'openai' não instalada. Execute: pip install openai")
            return self._simulate_generation()
        except Exception as e:
            print(f"❌ Erro ao chamar OpenAI: {e}")
            return self._simulate_generation()
    
    def _call_ollama(self, prompt):
        """Chama modelo local via Ollama"""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "codellama",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            return response.json()["response"]
        except ImportError:
            print("⚠️  Biblioteca 'requests' não instalada. Execute: pip install requests")
            return self._simulate_generation()
        except Exception as e:
            print(f"❌ Erro ao chamar Ollama: {e}")
            return self._simulate_generation()
    
    def _simulate_generation(self):
        """Simulação para quando não há API disponível"""
        return """fn transfer_funds(sender: &mut Account, receiver: &mut Account, amount: Gold) -> Result<(), TransferError> {
    // Guard: Validação de pré-condições
    if sender.balance < amount {
        return Err(TransferError::InsufficientFunds);
    }
    if amount <= 0 {
        return Err(TransferError::InvalidAmount);
    }
    
    let old_balance = sender.balance;
    
    // Solve: Execução otimizada para blockchain
    sender.balance -= amount;
    receiver.balance += amount;
    
    // Verify: Validação de pós-condições
    assert!(sender.balance < old_balance);
    
    Ok(())
}"""
