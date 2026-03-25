"""
Knowledge Store - v4.0.0
Storage and management for proven training seeds

"The Refinaria de Verdade"
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class KnowledgeStore:
    """
    Stores and manages proven code patterns for AI training
    
    Features:
    - Persistent storage in JSON format
    - Merkle root generation for integrity
    - Statistics tracking
    - Export to JSONL for training
    """
    
    def __init__(self, storage_dir: str = ".diotec360_knowledge"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.seeds_file = self.storage_dir / "training_seeds.json"
        self.seeds: List[Dict[str, Any]] = []
        self._load_seeds()
    
    def _load_seeds(self):
        """Load seeds from storage"""
        if self.seeds_file.exists():
            try:
                with open(self.seeds_file, 'r', encoding='utf-8') as f:
                    self.seeds = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load seeds: {e}")
                self.seeds = []
        else:
            self.seeds = []
    
    def _save_seeds(self):
        """Save seeds to storage"""
        try:
            with open(self.seeds_file, 'w', encoding='utf-8') as f:
                json.dump(self.seeds, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Failed to save seeds: {e}")
    
    def distill(self, seed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Distill (validate and sanitize) a training seed
        
        Returns:
            Distilled seed or None if validation fails
        """
        # Validate required fields
        required_fields = ['prompt', 'finalCode', 'judgeVerdict', 'category', 'language']
        for field in required_fields:
            if field not in seed:
                print(f"Validation failed: Missing field '{field}'")
                return None
        
        # Only accept PROVED seeds
        if seed['judgeVerdict'] != 'PROVED':
            print(f"Validation failed: Not PROVED (got {seed['judgeVerdict']})")
            return None
        
        # Generate unique ID
        seed_id = self._generate_id(seed['prompt'], seed['finalCode'])
        
        # Check for duplicates
        if any(s.get('id') == seed_id for s in self.seeds):
            print(f"Validation failed: Duplicate seed {seed_id}")
            return None
        
        # Create distilled seed
        distilled = {
            'id': seed_id,
            'timestamp': datetime.now().isoformat(),
            'prompt': seed['prompt'],
            'writerOutput': seed.get('writerOutput', ''),
            'criticReview': seed.get('criticReview', ''),
            'finalCode': seed['finalCode'],
            'judgeVerdict': seed['judgeVerdict'],
            'z3Proof': seed.get('z3Proof', ''),
            'writerProvider': seed.get('writerProvider', 'unknown'),
            'writerModel': seed.get('writerModel', 'unknown'),
            'criticProvider': seed.get('criticProvider', 'unknown'),
            'criticModel': seed.get('criticModel', 'unknown'),
            'category': seed['category'],
            'language': seed['language'],
            'complexity': seed.get('complexity', 'medium')
        }
        
        return distilled
    
    def store(self, seed: Dict[str, Any]) -> str:
        """
        Store a distilled seed and return Merkle root
        
        Returns:
            Merkle root hash
        """
        self.seeds.append(seed)
        self._save_seeds()
        
        # Generate Merkle root
        merkle_root = self._generate_merkle_root()
        
        return merkle_root
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(self.seeds),
            'byCategory': {},
            'byLanguage': {},
            'byComplexity': {},
            'byProvider': {}
        }
        
        for seed in self.seeds:
            # By category
            category = seed.get('category', 'other')
            stats['byCategory'][category] = stats['byCategory'].get(category, 0) + 1
            
            # By language
            language = seed.get('language', 'unknown')
            stats['byLanguage'][language] = stats['byLanguage'].get(language, 0) + 1
            
            # By complexity
            complexity = seed.get('complexity', 'medium')
            stats['byComplexity'][complexity] = stats['byComplexity'].get(complexity, 0) + 1
            
            # By provider
            provider = seed.get('writerProvider', 'unknown')
            stats['byProvider'][provider] = stats['byProvider'].get(provider, 0) + 1
        
        return stats
    
    def export_for_training(self, format: str = "jsonl") -> str:
        """
        Export seeds for AI training
        
        Args:
            format: Export format (jsonl, alpaca, sharegpt)
        
        Returns:
            Path to exported file
        """
        if format == "jsonl":
            output_file = self.storage_dir / "training_data.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for seed in self.seeds:
                    training_item = {
                        'prompt': seed['prompt'],
                        'completion': seed['finalCode'],
                        'metadata': {
                            'category': seed['category'],
                            'language': seed['language'],
                            'complexity': seed['complexity'],
                            'judgeVerdict': seed['judgeVerdict'],
                            'timestamp': seed['timestamp']
                        }
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
            
            return str(output_file)
        
        elif format == "alpaca":
            output_file = self.storage_dir / "training_data_alpaca.json"
            
            alpaca_data = []
            for seed in self.seeds:
                alpaca_data.append({
                    'instruction': seed['prompt'],
                    'input': '',
                    'output': seed['finalCode']
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(alpaca_data, f, indent=2, ensure_ascii=False)
            
            return str(output_file)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_id(self, prompt: str, code: str) -> str:
        """Generate unique ID for seed"""
        content = f"{prompt}{code}{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_merkle_root(self) -> str:
        """Generate Merkle root for all seeds"""
        if not self.seeds:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Hash each seed
        hashes = []
        for seed in self.seeds:
            seed_str = json.dumps(seed, sort_keys=True)
            seed_hash = hashlib.sha256(seed_str.encode()).hexdigest()
            hashes.append(seed_hash)
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last hash if odd
            
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            
            hashes = new_hashes
        
        return hashes[0]
