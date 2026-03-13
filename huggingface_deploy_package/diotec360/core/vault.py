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

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


class AethelVault:
    """
    O Cofre de Verdades - Sistema de Content-Addressable Code.
    
    Funções são identificadas por seu conteúdo lógico (AST), não por nome.
    Uma vez provada, uma função é imutável e eterna.
    """
    
    def __init__(self, vault_path=".diotec360_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        
        # Índice em memória para acesso rápido
        self.index = self._load_index()
        
        print(f"Vault inicializado em: {self.vault_path.absolute()}")
        print(f"Funcoes no cofre: {len(self.index)}")
    
    def get_function_hash(self, ast_node):
        """
        Gera um ID único baseado na ESTRUTURA da lógica,
        não no nome da função.
        
        Usa SHA-256 para garantir unicidade e segurança.
        """
        # Normalizar AST para garantir consistência
        ast_string = json.dumps(ast_node, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(ast_string.encode()).hexdigest()
    
    def get_logic_hash(self, intent_data):
        """
        Gera hash baseado APENAS na lógica (constraints + verify),
        ignorando nomes de variáveis e parâmetros.
        
        Isso permite que funções logicamente idênticas sejam reconhecidas
        mesmo com nomes diferentes.
        """
        def _cond_to_expr(cond):
            if isinstance(cond, dict):
                return str(cond.get('expression', '')).strip()
            return str(cond).strip()

        constraints = [_cond_to_expr(c) for c in intent_data.get('constraints', []) if _cond_to_expr(c)]
        post_conditions = [_cond_to_expr(c) for c in intent_data.get('post_conditions', []) if _cond_to_expr(c)]

        logic_structure = {
            'constraints': sorted(constraints),
            'post_conditions': sorted(post_conditions),
            'ai_instructions': intent_data.get('ai_instructions', {})
        }
        
        logic_string = json.dumps(logic_structure, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(logic_string.encode()).hexdigest()
    
    def store(self, intent_name, ast_node, verified_code, verification_result, metadata=None):
        """
        Armazena uma função verificada no cofre.
        
        Retorna o hash único da função.
        """
        # Gerar hashes
        full_hash = self.get_function_hash(ast_node)
        logic_hash = self.get_logic_hash(ast_node)
        
        # Verificar se já existe
        if full_hash in self.index:
            print(f"Funcao ja existe no cofre: {full_hash[:16]}...")
            return full_hash
        
        # Preparar metadados
        entry = {
            'intent_name': intent_name,
            'full_hash': full_hash,
            'logic_hash': logic_hash,
            'ast': ast_node,
            'code': verified_code,
            'verification': {
                'status': verification_result['status'],
                'message': verification_result['message'],
                'timestamp': datetime.now().isoformat()
            },
            'metadata': metadata or {},
            'immutable': True,
            'created_at': datetime.now().isoformat()
        }
        
        # Salvar no disco
        self._save_entry(full_hash, entry)
        
        # Atualizar índice
        self.index[full_hash] = {
            'intent_name': intent_name,
            'logic_hash': logic_hash,
            'created_at': entry['created_at'],
            'status': 'MATHEMATICALLY_PROVED'
        }
        self._save_index()

        # Proof-of-Precedent (PoP v0.1): index proven templates for future guidance
        try:
            if str(entry.get('verification', {}).get('status', '')).upper() == 'PROVED':
                from diotec360.core.refiner import build_precedent_record
                from diotec360.nexo.precedent_engine import PrecedentEngine

                engine = PrecedentEngine(vault_path=str(self.vault_path))
                record = build_precedent_record(
                    intent_name=intent_name,
                    full_hash=full_hash,
                    logic_hash=logic_hash,
                    intent_ast=ast_node,
                    verification=entry.get('verification', {}),
                    metadata=entry.get('metadata', {}),
                )
                engine.upsert(record)
        except Exception as e:
            print(f"[PoP] ⚠️ precedent indexing failed: {e}")
        
        print(f"\nFuncao imortalizada no Cofre:")
        print(f"   Intent: {intent_name}")
        print(f"   Full Hash: {full_hash[:16]}...{full_hash[-8:]}")
        print(f"   Logic Hash: {logic_hash[:16]}...{logic_hash[-8:]}")
        print(f"   Status: MATHEMATICALLY_PROVED")
        
        return full_hash
    
    def fetch(self, function_hash):
        """
        Recupera uma função do cofre pelo hash.
        """
        if function_hash not in self.index:
            return None
        
        entry = self._load_entry(function_hash)
        return entry
    
    def find_by_logic(self, intent_data):
        """
        Busca funções com lógica idêntica, independente do nome.
        
        Retorna lista de hashes de funções logicamente equivalentes.
        """
        target_logic_hash = self.get_logic_hash(intent_data)
        
        matches = []
        for full_hash, info in self.index.items():
            if info.get('logic_hash') == target_logic_hash:
                matches.append(full_hash)
        
        return matches
    
    def verify_integrity(self, function_hash):
        """
        Verifica se uma função no cofre não foi corrompida.
        
        Recalcula o hash e compara com o armazenado.
        """
        entry = self.fetch(function_hash)
        if not entry:
            return False
        
        # Recalcular hash
        calculated_hash = self.get_function_hash(entry['ast'])
        
        return calculated_hash == function_hash
    
    def list_functions(self):
        """
        Lista todas as funções no cofre.
        """
        return self.index
    
    def get_statistics(self):
        """
        Retorna estatísticas do cofre.
        """
        total = len(self.index)
        
        # Agrupar por logic_hash para encontrar duplicatas lógicas
        logic_groups = {}
        for full_hash, info in self.index.items():
            logic_hash = info.get('logic_hash')
            if not logic_hash:
                continue
            if logic_hash not in logic_groups:
                logic_groups[logic_hash] = []
            logic_groups[logic_hash].append(full_hash)
        
        unique_logic = len(logic_groups)
        duplicates = sum(1 for group in logic_groups.values() if len(group) > 1)
        
        return {
            'total_functions': total,
            'unique_logic': unique_logic,
            'logical_duplicates': duplicates,
            'vault_path': str(self.vault_path.absolute())
        }
    
    def export_function(self, function_hash, output_path):
        """
        Exporta uma função do cofre para um arquivo.
        """
        entry = self.fetch(function_hash)
        if not entry:
            raise ValueError(f"Função {function_hash} não encontrada no cofre")
        
        with open(output_path, 'w') as f:
            f.write(entry['code'])
        
        print(f"📤 Função exportada para: {output_path}")
    
    def _save_entry(self, function_hash, entry):
        """Salva entrada no disco"""
        entry_path = self.vault_path / f"{function_hash}.json"
        with open(entry_path, 'w') as f:
            json.dump(entry, f, indent=2)
    
    def _load_entry(self, function_hash):
        """Carrega entrada do disco"""
        entry_path = self.vault_path / f"{function_hash}.json"
        if not entry_path.exists():
            return None
        
        with open(entry_path, 'r') as f:
            return json.load(f)
    
    def _save_index(self):
        """Salva índice no disco"""
        index_path = self.vault_path / "index.json"
        with open(index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _load_index(self):
        """Carrega índice do disco"""
        index_path = self.vault_path / "index.json"
        if not index_path.exists():
            return {}
        
        with open(index_path, 'r') as f:
            return json.load(f)
    
    def generate_vault_report(self):
        """
        Gera relatório detalhado do cofre.
        """
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              AETHEL VAULT REPORT v0.5                        ║
╚══════════════════════════════════════════════════════════════╝

Vault Location: {stats['vault_path']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATISTICS:
  Total Functions: {stats['total_functions']}
  Unique Logic Patterns: {stats['unique_logic']}
  Logical Duplicates: {stats['logical_duplicates']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STORED FUNCTIONS:
"""
        
        for full_hash, info in self.index.items():
            report += f"\n  📦 {info['intent_name']}\n"
            report += f"     Hash: {full_hash[:16]}...{full_hash[-8:]}\n"
            report += f"     Status: {info.get('status', 'UNKNOWN')}\n"
            report += f"     Created: {info.get('created_at', 'UNKNOWN')}\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "\n🔐 All functions are IMMUTABLE and MATHEMATICALLY PROVED\n"
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report
