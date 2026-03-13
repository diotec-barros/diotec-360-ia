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
Aethel Cognitive Persistence - Memória de Destilação
Sistema que salva respostas verificadas para treinamento futuro do modelo local.

Este módulo implementa a memória do Neural Nexus: ele armazena todas as respostas
verificadas pelo Autonomous Distiller, organiza por categoria, e prepara datasets
para LoRA training.

Research Foundation:
- Knowledge Base Management
- Dataset Curation for Fine-tuning
- Deduplication Algorithms

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 4.0 "Neural Nexus"
Date: February 18, 2026
"""

import sqlite3
import json
import hashlib
import gzip
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import os


@dataclass
class StoredResponse:
    """
    Resposta armazenada no banco de dados.
    
    Attributes:
        id: ID único da resposta
        prompt: Prompt original
        response: Texto da resposta
        source: Fonte da resposta (ex: "gpt-4")
        category: Categoria (code, math, logic, text)
        response_type: Tipo específico (aethel_code, python_code, etc)
        confidence_score: Score de confiança (0.0-1.0)
        verification_passed: Se passou na verificação
        verification_details: Detalhes da verificação (JSON)
        timestamp: Timestamp de criação
        hash: Hash para deduplicação
    """
    id: Optional[str]
    prompt: str
    response: str
    source: str
    category: str
    response_type: str
    confidence_score: float
    verification_passed: bool
    verification_details: str
    timestamp: float
    hash: str


class CognitivePersistence:
    """
    Sistema de Persistência Cognitiva - Memória do Neural Nexus.
    
    Este sistema armazena todas as respostas verificadas pelo Autonomous Distiller
    e prepara datasets para LoRA training. Funcionalidades:
    
    - Armazenamento em SQLite com compressão
    - Deduplicação automática via hash
    - Organização por categoria
    - Índice de busca
    - Exportação para LoRA (JSON Lines)
    - Estatísticas de dataset
    
    Example:
        >>> persistence = CognitivePersistence("./cognitive_memory.db")
        >>> response_id = persistence.save_response(distilled_response)
        >>> stats = persistence.get_statistics()
        >>> if stats['total_responses'] >= 1000:
        ...     persistence.export_for_lora("./lora_dataset.jsonl")
    """
    
    def __init__(self, db_path: str = ".aethel_cognitive/memory.db"):
        """
        Inicializa Cognitive Persistence.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        
        # Criar diretório se não existe
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        print(f"[COGNITIVE] 💾 Cognitive Persistence inicializado")
        print(f"  Database: {db_path}")
    
    def _init_database(self) -> None:
        """Inicializa schema do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela principal de respostas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                response_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                verification_passed INTEGER NOT NULL,
                verification_details TEXT,
                timestamp REAL NOT NULL,
                hash TEXT NOT NULL UNIQUE
            )
        """)
        
        # Índices para busca rápida
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON responses(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification 
            ON responses(verification_passed)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_confidence 
            ON responses(confidence_score)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON responses(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def save_response(self, distilled_response) -> Optional[str]:
        """
        Salva resposta verificada no banco de dados.
        
        Args:
            distilled_response: DistilledResponse do Autonomous Distiller
        
        Returns:
            ID da resposta salva, ou None se duplicada
        """
        # Gerar hash para deduplicação
        content = f"{distilled_response.text}|{distilled_response.source}"
        response_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Verificar se já existe
        if self._exists(response_hash):
            print(f"[COGNITIVE] ⏭️  Resposta duplicada (hash: {response_hash[:8]}...)")
            return None
        
        # Gerar ID único
        response_id = hashlib.sha256(
            f"{response_hash}{distilled_response.timestamp}".encode()
        ).hexdigest()[:16]
        
        # Determinar categoria
        category = self._categorize(distilled_response.response_type)
        
        # Preparar dados
        stored = StoredResponse(
            id=response_id,
            prompt="",  # Prompt não está no DistilledResponse, usar vazio
            response=distilled_response.text,
            source=distilled_response.source,
            category=category,
            response_type=distilled_response.response_type.value,
            confidence_score=distilled_response.confidence_score,
            verification_passed=distilled_response.verification_passed,
            verification_details=json.dumps(distilled_response.verification_details),
            timestamp=distilled_response.timestamp,
            hash=response_hash
        )
        
        # Salvar no banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stored.id,
                stored.prompt,
                stored.response,
                stored.source,
                stored.category,
                stored.response_type,
                stored.confidence_score,
                1 if stored.verification_passed else 0,
                stored.verification_details,
                stored.timestamp,
                stored.hash
            ))
            
            conn.commit()
            
            print(f"[COGNITIVE] ✅ Resposta salva: {response_id}")
            print(f"  Categoria: {category}")
            print(f"  Fonte: {stored.source}")
            print(f"  Score: {stored.confidence_score:.3f}")
            
            return response_id
            
        except sqlite3.IntegrityError:
            print(f"[COGNITIVE] ⏭️  Resposta duplicada (ID: {response_id})")
            return None
        finally:
            conn.close()
    
    def _exists(self, response_hash: str) -> bool:
        """Verifica se resposta já existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM responses WHERE hash = ?", (response_hash,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def _categorize(self, response_type) -> str:
        """Categoriza resposta baseado no tipo"""
        # Converter Enum para string se necessário
        if hasattr(response_type, 'value'):
            type_str = response_type.value
        else:
            type_str = str(response_type)
        
        type_lower = type_str.lower()
        
        if "code" in type_lower:
            return "code"
        elif "math" in type_lower:
            return "math"
        elif "logic" in type_lower:
            return "logic"
        else:
            return "text"
    
    def get_by_category(self, category: str, limit: int = 100) -> List[StoredResponse]:
        """
        Recupera respostas por categoria.
        
        Args:
            category: Categoria (code, math, logic, text)
            limit: Máximo de respostas
        
        Returns:
            Lista de respostas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM responses 
            WHERE category = ? 
            ORDER BY confidence_score DESC 
            LIMIT ?
        """, (category, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_stored(row) for row in rows]
    
    def get_verified_only(self, min_confidence: float = 0.8, limit: int = 1000) -> List[StoredResponse]:
        """
        Recupera apenas respostas verificadas com alta confiança.
        
        Args:
            min_confidence: Score mínimo de confiança
            limit: Máximo de respostas
        
        Returns:
            Lista de respostas verificadas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM responses 
            WHERE verification_passed = 1 
            AND confidence_score >= ? 
            ORDER BY confidence_score DESC 
            LIMIT ?
        """, (min_confidence, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_stored(row) for row in rows]
    
    def _row_to_stored(self, row: tuple) -> StoredResponse:
        """Converte row do SQLite para StoredResponse"""
        return StoredResponse(
            id=row[0],
            prompt=row[1],
            response=row[2],
            source=row[3],
            category=row[4],
            response_type=row[5],
            confidence_score=row[6],
            verification_passed=bool(row[7]),
            verification_details=row[8],
            timestamp=row[9],
            hash=row[10]
        )
    
    def export_for_lora(self, output_path: str, min_confidence: float = 0.8) -> int:
        """
        Exporta dataset para formato LoRA (JSON Lines).
        
        Args:
            output_path: Caminho do arquivo de saída
            min_confidence: Score mínimo de confiança
        
        Returns:
            Número de exemplos exportados
        """
        print(f"\n[COGNITIVE] 📤 Exportando para LoRA...")
        print(f"  Output: {output_path}")
        print(f"  Min confidence: {min_confidence}")
        
        # Recuperar respostas verificadas
        responses = self.get_verified_only(min_confidence=min_confidence, limit=10000)
        
        if not responses:
            print("[COGNITIVE] ⚠️  Nenhuma resposta para exportar")
            return 0
        
        # Exportar em formato JSON Lines
        count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for resp in responses:
                # Formato LoRA: {"prompt": "...", "completion": "..."}
                example = {
                    "prompt": resp.prompt if resp.prompt else f"Generate {resp.category} code",
                    "completion": resp.response,
                    "metadata": {
                        "source": resp.source,
                        "category": resp.category,
                        "confidence": resp.confidence_score,
                        "timestamp": resp.timestamp
                    }
                }
                
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
                count += 1
        
        print(f"[COGNITIVE] ✅ {count} exemplos exportados")
        
        # Criar versão comprimida
        compressed_path = output_path + '.gz'
        with open(output_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        print(f"[COGNITIVE] 🗜️  Versão comprimida: {compressed_path}")
        
        return count

    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do dataset.
        
        Returns:
            Estatísticas completas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de respostas
        cursor.execute("SELECT COUNT(*) FROM responses")
        total = cursor.fetchone()[0]
        
        # Respostas verificadas
        cursor.execute("SELECT COUNT(*) FROM responses WHERE verification_passed = 1")
        verified = cursor.fetchone()[0]
        
        # Por categoria
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM responses 
            GROUP BY category
        """)
        by_category = dict(cursor.fetchall())
        
        # Por fonte
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM responses 
            GROUP BY source
        """)
        by_source = dict(cursor.fetchall())
        
        # Score médio
        cursor.execute("SELECT AVG(confidence_score) FROM responses")
        avg_score = cursor.fetchone()[0] or 0.0
        
        # Respostas de alta qualidade (score > 0.8)
        cursor.execute("""
            SELECT COUNT(*) FROM responses 
            WHERE confidence_score >= 0.8 AND verification_passed = 1
        """)
        high_quality = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_responses": total,
            "verified_responses": verified,
            "verification_rate": verified / total if total > 0 else 0.0,
            "by_category": by_category,
            "by_source": by_source,
            "average_confidence": avg_score,
            "high_quality_responses": high_quality,
            "ready_for_training": high_quality >= 1000,
            "training_threshold": 1000,
            "progress_to_training": min(1.0, high_quality / 1000)
        }
    
    def search(self, query: str, limit: int = 10) -> List[StoredResponse]:
        """
        Busca respostas por texto.
        
        Args:
            query: Texto de busca
            limit: Máximo de resultados
        
        Returns:
            Lista de respostas encontradas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Busca simples com LIKE
        cursor.execute("""
            SELECT * FROM responses 
            WHERE response LIKE ? OR prompt LIKE ?
            ORDER BY confidence_score DESC 
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_stored(row) for row in rows]
    
    def delete_low_quality(self, max_confidence: float = 0.5) -> int:
        """
        Remove respostas de baixa qualidade.
        
        Args:
            max_confidence: Score máximo para remoção
        
        Returns:
            Número de respostas removidas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM responses 
            WHERE confidence_score < ?
        """, (max_confidence,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"[COGNITIVE] 🗑️  {deleted} respostas de baixa qualidade removidas")
        
        return deleted
    
    def vacuum(self) -> None:
        """Otimiza banco de dados (VACUUM)"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
        
        print("[COGNITIVE] 🧹 Banco de dados otimizado")
    
    def backup(self, backup_path: str) -> None:
        """
        Cria backup do banco de dados.
        
        Args:
            backup_path: Caminho do backup
        """
        import shutil
        
        shutil.copy2(self.db_path, backup_path)
        
        print(f"[COGNITIVE] 💾 Backup criado: {backup_path}")
    
    def get_training_readiness(self) -> Dict[str, Any]:
        """
        Verifica se dataset está pronto para treinamento.
        
        Returns:
            Status de prontidão
        """
        stats = self.get_statistics()
        
        high_quality = stats['high_quality_responses']
        threshold = stats['training_threshold']
        
        ready = high_quality >= threshold
        progress = stats['progress_to_training']
        
        return {
            "ready": ready,
            "high_quality_count": high_quality,
            "threshold": threshold,
            "progress": progress,
            "remaining": max(0, threshold - high_quality),
            "message": (
                f"✅ Dataset pronto para treinamento! ({high_quality} exemplos)"
                if ready else
                f"⏳ Faltam {threshold - high_quality} exemplos de alta qualidade"
            )
        }


def create_persistence_from_env() -> CognitivePersistence:
    """
    Cria Cognitive Persistence a partir de variáveis de ambiente.
    
    Variável de ambiente:
    - AETHEL_COGNITIVE_DB: Caminho do banco de dados (default: .aethel_cognitive/memory.db)
    
    Returns:
        CognitivePersistence instance
    """
    db_path = os.getenv("AETHEL_COGNITIVE_DB", ".aethel_cognitive/memory.db")
    return CognitivePersistence(db_path)


if __name__ == "__main__":
    # Demo rápido
    print("=" * 80)
    print("AETHEL COGNITIVE PERSISTENCE - DEMO")
    print("=" * 80)
    
    # Criar persistence
    persistence = CognitivePersistence("./demo_cognitive.db")
    
    # Estatísticas iniciais
    stats = persistence.get_statistics()
    print(f"\n[DEMO] Estatísticas iniciais:")
    print(f"  Total de respostas: {stats['total_responses']}")
    print(f"  Respostas verificadas: {stats['verified_responses']}")
    print(f"  Taxa de verificação: {stats['verification_rate']:.1%}")
    
    # Verificar prontidão para treinamento
    readiness = persistence.get_training_readiness()
    print(f"\n[DEMO] Prontidão para treinamento:")
    print(f"  {readiness['message']}")
    print(f"  Progresso: {readiness['progress']:.1%}")
    
    print("\n🏛️ [COGNITIVE PERSISTENCE: OPERATIONAL]")
