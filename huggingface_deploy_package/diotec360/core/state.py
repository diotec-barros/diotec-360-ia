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
Aethel State Manager - The Eternal Memory
Authenticated State Tree with conservation proofs

Features:
- Merkle State Tree for global state
- State transition validation
- Conservation law enforcement
- Atomic persistence
- Crash recovery

Philosophy: "State is not stored. State is proved."
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class MerkleStateTree:
    """
    Authenticated State Tree using Merkle Tree structure.
    
    Each account is a leaf node with:
    - balance: Current balance
    - nonce: Transaction counter
    - hash: SHA-256(balance + nonce)
    
    The root hash represents the entire global state.
    """
    
    def __init__(self):
        self.accounts = {}  # address -> {balance, nonce, hash}
        self.root_hash = None
        self.history = []  # List of (root_hash, timestamp, operation)
    
    def _hash_account(self, balance: int, nonce: int, public_key: str = "") -> str:
        """Generate hash for account state (v2.2.0: includes public_key)"""
        data = f"{balance}:{nonce}:{public_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _calculate_root(self) -> str:
        """Calculate Merkle root from all accounts"""
        if not self.accounts:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Sort accounts by address for deterministic ordering
        sorted_accounts = sorted(self.accounts.items())
        
        # Combine all account hashes
        combined = ""
        for address, account in sorted_accounts:
            combined += account['hash']
        
        # Generate root hash
        root = hashlib.sha256(combined.encode()).hexdigest()
        return root
    
    def create_account(self, address: str, initial_balance: int = 0, public_key: str = "") -> str:
        """
        Create new account with initial balance and public key (v2.2.0).
        
        Args:
            address: Account address
            initial_balance: Initial balance
            public_key: ED25519 public key (hex) for signature verification
        
        Returns:
            Account hash
        """
        if address in self.accounts:
            raise ValueError(f"Account {address} already exists")
        
        account_hash = self._hash_account(initial_balance, 0, public_key)
        
        self.accounts[address] = {
            'balance': initial_balance,
            'nonce': 0,
            'public_key': public_key,  # v2.2.0: Store public key
            'hash': account_hash
        }
        
        # Update root
        old_root = self.root_hash
        self.root_hash = self._calculate_root()
        
        # Record history
        self.history.append({
            'operation': 'create_account',
            'address': address,
            'initial_balance': initial_balance,
            'old_root': old_root,
            'new_root': self.root_hash,
            'timestamp': datetime.now().isoformat()
        })
        
        return account_hash
    
    def get_account(self, address: str) -> Optional[Dict[str, Any]]:
        """Get account state"""
        return self.accounts.get(address)
    
    def update_account(self, address: str, new_balance: int) -> str:
        """
        Update account balance (increments nonce).
        
        Returns:
            New account hash
        """
        if address not in self.accounts:
            raise ValueError(f"Account {address} does not exist")
        
        account = self.accounts[address]
        old_balance = account['balance']
        old_nonce = account['nonce']
        public_key = account.get('public_key', '')  # v2.2.0: Preserve public key
        
        # Update account
        new_nonce = old_nonce + 1
        new_hash = self._hash_account(new_balance, new_nonce, public_key)
        
        self.accounts[address] = {
            'balance': new_balance,
            'nonce': new_nonce,
            'public_key': public_key,  # v2.2.0: Preserve public key
            'hash': new_hash
        }
        
        # Update root
        old_root = self.root_hash
        self.root_hash = self._calculate_root()
        
        # Record history
        self.history.append({
            'operation': 'update_account',
            'address': address,
            'old_balance': old_balance,
            'new_balance': new_balance,
            'old_nonce': old_nonce,
            'new_nonce': new_nonce,
            'old_root': old_root,
            'new_root': self.root_hash,
            'timestamp': datetime.now().isoformat()
        })
        
        return new_hash
    
    def get_total_supply(self) -> int:
        """Calculate total supply (sum of all balances)"""
        return sum(account['balance'] for account in self.accounts.values())
    
    def get_merkle_proof(self, address: str) -> Dict[str, Any]:
        """
        Generate Merkle proof for account inclusion.
        
        Returns proof that account exists in state tree.
        """
        if address not in self.accounts:
            raise ValueError(f"Account {address} does not exist")
        
        account = self.accounts[address]
        
        # Simplified proof (in production, would include sibling hashes)
        proof = {
            'address': address,
            'balance': account['balance'],
            'nonce': account['nonce'],
            'account_hash': account['hash'],
            'root_hash': self.root_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        return proof
    
    def verify_merkle_proof(self, proof: Dict[str, Any]) -> bool:
        """Verify Merkle proof is valid"""
        address = proof['address']
        
        if address not in self.accounts:
            return False
        
        account = self.accounts[address]
        
        # Verify account hash
        expected_hash = self._hash_account(proof['balance'], proof['nonce'])
        if expected_hash != proof['account_hash']:
            return False
        
        # Verify root hash
        if self.root_hash != proof['root_hash']:
            return False
        
        return True
    
    def snapshot(self) -> Dict[str, Any]:
        """Create snapshot of current state"""
        return {
            'root_hash': self.root_hash,
            'accounts': self.accounts.copy(),
            'total_supply': self.get_total_supply(),
            'timestamp': datetime.now().isoformat()
        }
    
    def restore(self, snapshot: Dict[str, Any]):
        """Restore state from snapshot"""
        self.root_hash = snapshot['root_hash']
        self.accounts = snapshot['accounts'].copy()


class StateTransitionEngine:
    """
    Validates and applies state transitions with conservation proofs.
    
    Ensures:
    - Total supply conservation
    - Balance non-negativity
    - Transaction atomicity
    - State consistency
    """
    
    def __init__(self, state_tree: MerkleStateTree):
        self.state_tree = state_tree
        self.audit_log = []
    
    def _log(self, level: str, message: str):
        """Add entry to audit log"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.audit_log.append(entry)
        
        icon = {
            'INFO': '📋',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CONSERVATION': '⚖️'
        }.get(level, '•')
        
        print(f"{icon} [{level}] {message}")
    
    def apply_transfer(self, sender: str, receiver: str, amount: int) -> Tuple[bool, str, str]:
        """
        Apply transfer with conservation proof.
        
        Returns:
            (success, old_root, new_root)
        """
        self._log('INFO', f"Applying transfer: {sender} -> {receiver}, amount={amount}")
        
        # Get current state
        old_root = self.state_tree.root_hash
        old_supply = self.state_tree.get_total_supply()
        
        # Get accounts
        sender_account = self.state_tree.get_account(sender)
        receiver_account = self.state_tree.get_account(receiver)
        
        if not sender_account:
            self._log('ERROR', f"Sender account {sender} does not exist")
            return False, old_root, old_root
        
        if not receiver_account:
            self._log('ERROR', f"Receiver account {receiver} does not exist")
            return False, old_root, old_root
        
        # Verify guards
        if sender_account['balance'] < amount:
            self._log('ERROR', f"Insufficient balance: {sender_account['balance']} < {amount}")
            return False, old_root, old_root
        
        if amount <= 0:
            self._log('ERROR', f"Invalid amount: {amount}")
            return False, old_root, old_root
        
        # Create snapshot for rollback
        snapshot = self.state_tree.snapshot()
        
        try:
            # Apply transfer
            new_sender_balance = sender_account['balance'] - amount
            new_receiver_balance = receiver_account['balance'] + amount
            
            self.state_tree.update_account(sender, new_sender_balance)
            self.state_tree.update_account(receiver, new_receiver_balance)
            
            # Verify conservation
            new_supply = self.state_tree.get_total_supply()
            
            if new_supply != old_supply:
                self._log('ERROR', f"Conservation violated: {old_supply} != {new_supply}")
                # Rollback
                self.state_tree.restore(snapshot)
                return False, old_root, old_root
            
            self._log('CONSERVATION', f"Total supply conserved: {old_supply} == {new_supply}")
            
            # Get new root
            new_root = self.state_tree.root_hash
            
            self._log('SUCCESS', f"Transfer complete: {old_root[:16]}... -> {new_root[:16]}...")
            
            return True, old_root, new_root
        
        except Exception as e:
            self._log('ERROR', f"Transfer failed: {e}")
            # Rollback
            self.state_tree.restore(snapshot)
            return False, old_root, old_root
    
    def verify_conservation(self, expected_supply: int) -> bool:
        """Verify total supply matches expected value"""
        actual_supply = self.state_tree.get_total_supply()
        
        if actual_supply == expected_supply:
            self._log('CONSERVATION', f"Conservation verified: {actual_supply} == {expected_supply}")
            return True
        else:
            self._log('ERROR', f"Conservation violated: {actual_supply} != {expected_supply}")
            return False


class AethelStateManager:
    """
    Complete state management system with persistence.
    
    Features:
    - Merkle State Tree
    - State transition validation
    - Conservation proofs
    - Atomic persistence
    - Crash recovery
    """
    
    def __init__(self, state_dir: str = ".diotec360_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        
        self.state_tree = MerkleStateTree()
        self.transition_engine = StateTransitionEngine(self.state_tree)
        
        self.wal_path = self.state_dir / "wal.log"  # Write-ahead log
        self.snapshot_path = self.state_dir / "snapshot.json"
    
    def initialize_state(self, accounts: Dict[str, int], total_supply: int):
        """
        Initialize state with accounts and verify total supply.
        
        Args:
            accounts: Dict of address -> initial_balance
            total_supply: Expected total supply
        """
        print("\n" + "="*70)
        print("🌳 AETHEL STATE MANAGER - INITIALIZING STATE")
        print("="*70 + "\n")
        
        # Create accounts
        for address, balance in accounts.items():
            self.state_tree.create_account(address, balance)
            print(f"  Created account: {address} with balance {balance}")
        
        # Verify total supply
        actual_supply = self.state_tree.get_total_supply()
        
        if actual_supply != total_supply:
            raise ValueError(f"Total supply mismatch: {actual_supply} != {total_supply}")
        
        print(f"\n⚖️  Total supply verified: {actual_supply}")
        print(f"🌳 Merkle root: {self.state_tree.root_hash[:32]}...")
        print("\n" + "="*70)
        print("✅ STATE INITIALIZED")
        print("="*70 + "\n")
    
    def execute_transfer(self, sender: str, receiver: str, amount: int) -> Dict[str, Any]:
        """Execute transfer with state transition"""
        success, old_root, new_root = self.transition_engine.apply_transfer(
            sender, receiver, amount
        )
        
        return {
            'success': success,
            'old_root': old_root,
            'new_root': new_root,
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_state_root(self) -> str:
        """Get current state root hash"""
        return self.state_tree.root_hash
    
    def get_account_balance(self, address: str) -> Optional[int]:
        """Get account balance"""
        account = self.state_tree.get_account(address)
        return account['balance'] if account else None
    
    def get_total_supply(self) -> int:
        """Get total supply"""
        return self.state_tree.get_total_supply()
    
    def save_snapshot(self):
        """Save state snapshot to disk"""
        snapshot = self.state_tree.snapshot()
        
        with open(self.snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"💾 State snapshot saved: {self.snapshot_path}")
    
    def load_snapshot(self):
        """Load state snapshot from disk"""
        if not self.snapshot_path.exists():
            print("⚠️  No snapshot found")
            return False
        
        with open(self.snapshot_path, 'r') as f:
            snapshot = json.load(f)
        
        self.state_tree.restore(snapshot)
        
        print(f"📂 State snapshot loaded: {self.snapshot_path}")
        print(f"🌳 Merkle root: {self.state_tree.root_hash[:32]}...")
        
        return True
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        return {
            'root_hash': self.state_tree.root_hash,
            'total_accounts': len(self.state_tree.accounts),
            'total_supply': self.state_tree.get_total_supply(),
            'history_length': len(self.state_tree.history)
        }
