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
from dataclasses import dataclass, asdict


@dataclass
class MerkleProof:
    """Merkle proof structure for interaction verification"""
    account_hash: str
    root_hash: str


@dataclass
class InteractionNode:
    """
    Data class representing an AI interaction in the Merkle Tree.
    
    Fields map from SQLite (ANGO IA) to Merkle Tree (DIOTEC 360):
    - interaction_id: UUID v4 identifier
    - timestamp: Unix timestamp (int)
    - critic_provider: Provider name (ollama/openai/anthropic)
    - critic_model: Model identifier
    - command: Command executed (generate/refactor)
    - context_hash: SHA-256 hash of the context
    - response_size: Size of response in characters
    - judge_verdict: Verdict from Judge (certified/unverified)
    - judge_message: Message from Judge
    - merkle_proof: Nested proof object with account_hash and root_hash
    """
    interaction_id: str
    timestamp: int
    critic_provider: str
    critic_model: str
    command: str
    context_hash: str
    response_size: int
    judge_verdict: str
    judge_message: str
    merkle_proof: Optional[MerkleProof] = None
    
    def calculate_hash(self) -> str:
        """
        Calculate SHA-256 hash of the interaction.
        
        Hash includes all fields except merkle_proof.
        Uses deterministic JSON serialization with sorted keys.
        
        Returns:
            SHA-256 hash as hexadecimal string
        """
        # Create dictionary with all fields except merkle_proof
        data = {
            'interaction_id': self.interaction_id,
            'timestamp': self.timestamp,
            'critic_provider': self.critic_provider,
            'critic_model': self.critic_model,
            'command': self.command,
            'context_hash': self.context_hash,
            'response_size': self.response_size,
            'judge_verdict': self.judge_verdict,
            'judge_message': self.judge_message
        }
        
        # Serialize to JSON with sorted keys for determinism
        json_str = json.dumps(data, sort_keys=True)
        
        # Calculate SHA-256 hash
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def to_json(self) -> str:
        """
        Serialize InteractionNode to JSON string.
        
        Returns:
            JSON string representation
        """
        data = asdict(self)
        # Convert MerkleProof to dict if present
        if self.merkle_proof:
            data['merkle_proof'] = {
                'account_hash': self.merkle_proof.account_hash,
                'root_hash': self.merkle_proof.root_hash
            }
        return json.dumps(data, sort_keys=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'InteractionNode':
        """
        Deserialize InteractionNode from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            InteractionNode instance
        """
        data = json.loads(json_str)
        
        # Convert merkle_proof dict to MerkleProof object if present
        if data.get('merkle_proof'):
            proof_data = data['merkle_proof']
            data['merkle_proof'] = MerkleProof(
                account_hash=proof_data['account_hash'],
                root_hash=proof_data['root_hash']
            )
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert InteractionNode to dictionary.
        
        Returns:
            Dictionary representation
        """
        data = asdict(self)
        # Convert MerkleProof to dict if present
        if self.merkle_proof:
            data['merkle_proof'] = {
                'account_hash': self.merkle_proof.account_hash,
                'root_hash': self.merkle_proof.root_hash
            }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionNode':
        """
        Create InteractionNode from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            InteractionNode instance
        """
        # Convert merkle_proof dict to MerkleProof object if present
        if data.get('merkle_proof'):
            proof_data = data['merkle_proof']
            data['merkle_proof'] = MerkleProof(
                account_hash=proof_data['account_hash'],
                root_hash=proof_data['root_hash']
            )
        
        return cls(**data)


def calculate_interaction_hash(interaction: InteractionNode) -> str:
    """
    Calculate SHA-256 hash of an interaction.
    
    Hash includes all fields except merkle_proof.
    Uses deterministic JSON serialization with sorted keys.
    
    Args:
        interaction: InteractionNode instance to hash
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    return interaction.calculate_hash()


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
        self.communication_logs = {}  # public_key -> CommunicationAccount
        self.root_hash = None
        self.history = []  # List of (root_hash, timestamp, operation)
    
    def _hash_account(self, balance: int, nonce: int, public_key: str = "") -> str:
        """Generate hash for account state (v2.2.0: includes public_key)"""
        data = f"{balance}:{nonce}:{public_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _hash_communication_account(self, public_key: str, interaction_count: int, 
                                     last_sync_timestamp: int, interactions: List[Dict[str, Any]]) -> str:
        """Generate hash for communication account state"""
        # Create deterministic hash from communication account data
        interactions_hash = hashlib.sha256(
            json.dumps(interactions, sort_keys=True).encode()
        ).hexdigest()
        data = f"{public_key}:{interaction_count}:{last_sync_timestamp}:{interactions_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _calculate_root(self) -> str:
        """Calculate Merkle root from all accounts and communication logs"""
        if not self.accounts and not self.communication_logs:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Sort accounts by address for deterministic ordering
        sorted_accounts = sorted(self.accounts.items())
        
        # Combine all account hashes
        accounts_combined = ""
        for address, account in sorted_accounts:
            accounts_combined += account['hash']
        
        # Sort communication logs by public_key for deterministic ordering
        sorted_comm_logs = sorted(self.communication_logs.items())
        
        # Combine all communication log hashes
        comm_logs_combined = ""
        for public_key, comm_account in sorted_comm_logs:
            comm_logs_combined += comm_account['hash']
        
        # Combine both trees
        combined = accounts_combined + comm_logs_combined
        
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
    
    def create_communication_account(self, public_key: str) -> str:
        """
        Create new communication account for AI interactions.
        
        Args:
            public_key: ED25519 public key (hex) for the user
        
        Returns:
            Communication account hash
        """
        if public_key in self.communication_logs:
            raise ValueError(f"Communication account for {public_key} already exists")
        
        # Initialize empty communication account
        interactions = []
        interaction_count = 0
        last_sync_timestamp = 0
        
        account_hash = self._hash_communication_account(
            public_key, interaction_count, last_sync_timestamp, interactions
        )
        
        self.communication_logs[public_key] = {
            'public_key': public_key,
            'interaction_count': interaction_count,
            'last_sync_timestamp': last_sync_timestamp,
            'interactions': interactions,
            'hash': account_hash
        }
        
        # Update root
        old_root = self.root_hash
        self.root_hash = self._calculate_root()
        
        # Record history
        self.history.append({
            'operation': 'create_communication_account',
            'public_key': public_key,
            'old_root': old_root,
            'new_root': self.root_hash,
            'timestamp': datetime.now().isoformat()
        })
        
        return account_hash
    
    def get_communication_account(self, public_key: str) -> Optional[Dict[str, Any]]:
        """Get communication account state"""
        return self.communication_logs.get(public_key)
    def add_interaction(self, public_key: str, interaction: Dict[str, Any]) -> Tuple[str, str]:
            """
            Add interaction to communication account with conflict resolution.

            Args:
                public_key: ED25519 public key (hex) for the user
                interaction: Interaction data dictionary

            Returns:
                Tuple of (account_hash, root_hash)

            Raises:
                ValueError: If interaction_id already exists with different content (409 Conflict)
            """
            import time
            import logging

            logger = logging.getLogger(__name__)

            # Get or create communication account
            if public_key not in self.communication_logs:
                self.create_communication_account(public_key)

            comm_account = self.communication_logs[public_key]

            # Task 5.1: Check for existing interaction_id (conflict resolution)
            interaction_id = interaction.get('interaction_id')
            existing_interaction = None

            if interaction_id:
                for existing in comm_account['interactions']:
                    if existing.get('interaction_id') == interaction_id:
                        existing_interaction = existing
                        break

            if existing_interaction:
                # Compare content (exclude merkle_proof if present)
                def normalize_for_comparison(data: Dict[str, Any]) -> Dict[str, Any]:
                    """Remove merkle_proof for comparison"""
                    normalized = data.copy()
                    normalized.pop('merkle_proof', None)
                    return normalized

                existing_normalized = normalize_for_comparison(existing_interaction)
                new_normalized = normalize_for_comparison(interaction)

                if existing_normalized == new_normalized:
                    # Idempotent case: content matches, return existing proof
                    logger.info(
                        f"Idempotent sync for interaction_id={interaction_id}, "
                        f"public_key={public_key[:8]}..."
                    )
                    return comm_account['hash'], self.root_hash
                else:
                    # Conflict case: content differs
                    logger.warning(
                        f"CONFLICT DETECTED: interaction_id={interaction_id} already exists "
                        f"with different content for public_key={public_key[:8]}... "
                        f"Existing: {existing_normalized}, New: {new_normalized}"
                    )
                    raise ValueError(
                        f"Conflict: interaction_id {interaction_id} already exists with different content"
                    )

            # Append interaction to list
            comm_account['interactions'].append(interaction)

            # Increment interaction count
            comm_account['interaction_count'] += 1

            # Update last sync timestamp to current Unix timestamp
            comm_account['last_sync_timestamp'] = int(time.time())

            # Recalculate account hash
            new_account_hash = self._hash_communication_account(
                comm_account['public_key'],
                comm_account['interaction_count'],
                comm_account['last_sync_timestamp'],
                comm_account['interactions']
            )

            comm_account['hash'] = new_account_hash

            # Update communication_logs reference
            self.communication_logs[public_key] = comm_account

            # Recalculate Merkle root
            old_root = self.root_hash
            self.root_hash = self._calculate_root()

            # Record history
            self.history.append({
                'operation': 'add_interaction',
                'public_key': public_key,
                'interaction_id': interaction.get('interaction_id', 'unknown'),
                'old_root': old_root,
                'new_root': self.root_hash,
                'timestamp': datetime.now().isoformat()
            })

            return new_account_hash, self.root_hash


    
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
            'communication_logs': self.communication_logs.copy(),
            'total_supply': self.get_total_supply(),
            'timestamp': datetime.now().isoformat()
        }
    
    def restore(self, snapshot: Dict[str, Any]):
        """Restore state from snapshot"""
        self.root_hash = snapshot['root_hash']
        self.accounts = snapshot['accounts'].copy()
        # v3.3.0: Restore communication_logs if present
        if 'communication_logs' in snapshot:
            self.communication_logs = snapshot['communication_logs'].copy()


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
    
    def __init__(self, state_dir: str = ".aethel_state"):
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
