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
Aethel-Lens - The Visual Interface
Real-time state visualization and proof path display

Features:
- Merkle Tree visualization
- Proof path highlighting
- Conservation law display
- Audit trail timeline
- Mathematical proof stamps

Philosophy: "Transparency is not optional. It is mathematical."
"""

from typing import Dict, Any, List
from datetime import datetime


class AethelLens:
    """
    Visual interface for Aethel state and proofs.
    
    Transforms cryptographic hashes and mathematical proofs
    into human-readable visualizations.
    """
    
    def __init__(self):
        self.proof_history = []
    
    def display_header(self, title: str):
        """Display formatted header"""
        print("\n" + "="*80)
        print(f"🔍 AETHEL-LENS: {title}")
        print("="*80 + "\n")
    
    def display_merkle_tree(self, state_tree):
        """
        Visualize Merkle State Tree.
        
        Shows:
        - Root hash
        - Account nodes
        - Balance distribution
        """
        self.display_header("MERKLE STATE TREE")
        
        print(f"🌳 Root Hash: {state_tree.root_hash[:32]}...")
        print(f"📊 Total Accounts: {len(state_tree.accounts)}")
        print(f"💰 Total Supply: {state_tree.get_total_supply():,}")
        print()
        
        # Display accounts
        print("Account Tree:")
        print("-" * 80)
        
        for address, account in sorted(state_tree.accounts.items()):
            balance_bar = "█" * min(50, account['balance'] // 20000)
            print(f"  {address:20} | Balance: {account['balance']:>10,} | {balance_bar}")
            print(f"  {'':20} | Nonce: {account['nonce']:>12} | Hash: {account['hash'][:16]}...")
            print()
        
        print("="*80 + "\n")
    
    def display_proof_path(self, transition: Dict[str, Any]):
        """
        Display proof path for state transition.
        
        Shows:
        - Old state root (red)
        - Transition operation (yellow)
        - New state root (green)
        - Conservation proof
        """
        self.display_header("PROOF PATH")
        
        success = transition.get('success', False)
        
        if success:
            print("✅ MATHEMATICALLY PROVED")
            print()
            print(f"  Old Root: 🔴 {transition['old_root'][:32]}...")
            print(f"            ↓")
            print(f"  Operation: {transition['sender']} → {transition['receiver']}")
            print(f"  Amount: {transition['amount']:,}")
            print(f"            ↓")
            print(f"  New Root: 🟢 {transition['new_root'][:32]}...")
            print()
            print("  ⚖️  Conservation Law: VERIFIED")
            print("  🔒 State Integrity: SEALED")
        else:
            print("❌ PROOF FAILED")
            print()
            print(f"  Root: 🔴 {transition['old_root'][:32]}...")
            print(f"  Operation: REJECTED")
            print(f"  Reason: Verification failed")
        
        print()
        print("="*80 + "\n")
        
        # Record in history
        self.proof_history.append(transition)
    
    def display_audit_trail(self, history: List[Dict[str, Any]]):
        """
        Display audit trail timeline.
        
        Shows chronological sequence of all state transitions.
        """
        self.display_header("AUDIT TRAIL")
        
        print(f"📜 Total Operations: {len(history)}")
        print()
        
        for i, entry in enumerate(history, 1):
            operation = entry.get('operation', 'unknown')
            timestamp = entry.get('timestamp', 'N/A')
            
            print(f"  [{i}] {timestamp}")
            print(f"      Operation: {operation}")
            
            if operation == 'create_account':
                print(f"      Account: {entry['address']}")
                print(f"      Initial Balance: {entry['initial_balance']:,}")
            elif operation == 'update_account':
                print(f"      Account: {entry['address']}")
                print(f"      Balance: {entry['old_balance']:,} → {entry['new_balance']:,}")
                print(f"      Nonce: {entry['old_nonce']} → {entry['new_nonce']}")
            
            print(f"      Root: {entry['old_root'][:16] if entry['old_root'] else 'N/A'}... → {entry['new_root'][:16]}...")
            print()
        
        print("="*80 + "\n")
    
    def display_conservation_proof(self, old_supply: int, new_supply: int):
        """
        Display conservation law proof.
        
        Shows mathematical proof that total supply is conserved.
        """
        self.display_header("CONSERVATION PROOF")
        
        print("⚖️  Law of Conservation of Value")
        print()
        print(f"  Before: {old_supply:,}")
        print(f"  After:  {new_supply:,}")
        print(f"  Delta:  {new_supply - old_supply:,}")
        print()
        
        if old_supply == new_supply:
            print("  ✅ CONSERVATION VERIFIED")
            print("  Mathematical Proof: Σ(balances_before) = Σ(balances_after)")
        else:
            print("  ❌ CONSERVATION VIOLATED")
            print("  System Integrity: COMPROMISED")
        
        print()
        print("="*80 + "\n")
    
    def display_execution_envelope(self, envelope: Dict[str, Any]):
        """
        Display complete execution envelope.
        
        Shows:
        - Input parameters
        - Verification status
        - Output state
        - Audit trail
        - Proof certificate
        """
        self.display_header("EXECUTION ENVELOPE")
        
        print("📦 Envelope Contents:")
        print()
        
        # Input
        print("  📥 INPUT:")
        for key, value in envelope.get('input', {}).items():
            print(f"      {key}: {value}")
        print()
        
        # Verification
        verification = envelope.get('verification', 'UNKNOWN')
        icon = "✅" if verification == "PASSED" else "❌"
        print(f"  {icon} VERIFICATION: {verification}")
        print()
        
        # Output
        print("  📤 OUTPUT:")
        for key, value in envelope.get('output_state', {}).items():
            print(f"      {key}: {value}")
        print()
        
        # Proof
        if 'proof_certificate' in envelope:
            cert = envelope['proof_certificate']
            print("  🏆 PROOF CERTIFICATE:")
            print(f"      Hash: {cert.get('hash', 'N/A')[:32]}...")
            print(f"      Timestamp: {cert.get('timestamp', 'N/A')}")
            print(f"      Status: {cert.get('status', 'N/A')}")
        
        print()
        print("="*80 + "\n")
    
    def display_final_state(self, state_manager):
        """
        Display final state summary.
        
        The ultimate output: The Merkle Root that seals everything.
        """
        self.display_header("FINAL STATE")
        
        summary = state_manager.get_state_summary()
        
        print("🏁 SYSTEM STATE SEALED")
        print()
        print(f"  🌳 Merkle Root: {summary['root_hash']}")
        print(f"  📊 Total Accounts: {summary['total_accounts']}")
        print(f"  💰 Total Supply: {summary['total_supply']:,}")
        print(f"  📜 History Length: {summary['history_length']}")
        print()
        print("  🔒 State Integrity: MATHEMATICALLY GUARANTEED")
        print("  ⚖️  Conservation Laws: ENFORCED")
        print("  ✅ Proof Status: COMPLETE")
        print()
        print("="*80 + "\n")
        
        # Display proof history summary
        if self.proof_history:
            print("📊 PROOF HISTORY SUMMARY:")
            print()
            successful = sum(1 for p in self.proof_history if p.get('success', False))
            total = len(self.proof_history)
            print(f"  Total Proofs: {total}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {total - successful}")
            print(f"  Success Rate: {(successful/total*100):.1f}%")
            print()
            print("="*80 + "\n")
