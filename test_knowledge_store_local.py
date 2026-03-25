"""
Test Knowledge Store Locally - v4.0.0
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from diotec360.ai.knowledge_store import KnowledgeStore

def test_knowledge_store():
    """Test the knowledge store locally"""
    
    print("=" * 80)
    print("🧠 TESTING KNOWLEDGE STORE v4.0.0 (LOCAL)")
    print("=" * 80)
    
    # Initialize store
    print("\n[1/5] Initializing Knowledge Store...")
    store = KnowledgeStore(storage_dir=".test_knowledge")
    print(f"✅ Store initialized")
    
    # Get initial stats
    print("\n[2/5] Getting Initial Stats...")
    stats = store.get_stats()
    print(f"✅ Initial patterns: {stats['total']}")
    
    # Create test seed
    print("\n[3/5] Creating Test Seed...")
    seed = {
        "prompt": "Create a secure deposit function",
        "writerOutput": "intent secure_deposit(amount: decimal) -> bool { ... }",
        "criticReview": "Looks good",
        "finalCode": "intent secure_deposit(amount: decimal, account_id: string) -> bool {\n  require amount > 0;\n  return true;\n}",
        "judgeVerdict": "PROVED",
        "z3Proof": "All assertions verified",
        "writerProvider": "test",
        "writerModel": "test-v1",
        "criticProvider": "test",
        "criticModel": "test-critic",
        "category": "financial",
        "language": "diotec360",
        "complexity": "medium"
    }
    print(f"✅ Test seed created")
    
    # Distill seed
    print("\n[4/5] Distilling Seed...")
    distilled = store.distill(seed)
    if distilled:
        print(f"✅ Seed distilled: {distilled['id']}")
        
        # Store seed
        merkle_root = store.store(distilled)
        print(f"✅ Seed stored with Merkle root: {merkle_root[:32]}...")
    else:
        print(f"❌ Distillation failed")
        return False
    
    # Get updated stats
    print("\n[5/5] Getting Updated Stats...")
    stats = store.get_stats()
    print(f"✅ Total patterns: {stats['total']}")
    print(f"   By Category: {stats['byCategory']}")
    print(f"   By Language: {stats['byLanguage']}")
    print(f"   By Complexity: {stats['byComplexity']}")
    
    # Export
    print("\n[BONUS] Exporting Training Data...")
    output_path = store.export_for_training(format="jsonl")
    print(f"✅ Exported to: {output_path}")
    
    print("\n" + "=" * 80)
    print("🎉 KNOWLEDGE STORE: OPERATIONAL")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_knowledge_store()
    exit(0 if success else 1)
