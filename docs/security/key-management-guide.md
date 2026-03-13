# Security Key Management Guide - RVC v2 Hardening

## Version: v1.9.2 "The Hardening"
## Audience: Security Administrators

---

## Overview

RVC v2 introduces **Sovereign Gossip** (RVC2-006) with ED25519 signature verification for all P2P messages. This guide covers key generation, distribution, rotation, and security best practices.

**Security Principle**: "Every message is signed. Every signature is verified. No exceptions."

---

## ED25519 Key Pairs

### Key Properties

- **Algorithm**: ED25519 (Edwards-curve Digital Signature Algorithm)
- **Key Size**: 256 bits (32 bytes)
- **Signature Size**: 512 bits (64 bytes)
- **Performance**: ~0.5ms signing, ~1ms verification
- **Security**: 128-bit security level (equivalent to RSA-3072)

### Key Components

```python
# Public Key (32 bytes)
public_key = b'\x12\x34\x56...'  # Shared with all nodes

# Private Key (32 bytes)
private_key = b'\xab\xcd\xef...'  # KEEP SECRET!

# Node ID (derived from public key)
node_id = hashlib.sha256(public_key).hexdigest()[:16]
```

---

## Key Generation

### Generate New Key Pair

```python
from diotec360.core.crypto import ED25519Signer
import secrets

def generate_node_keys(node_id: str):
    """Generate ED25519 key pair for a node"""
    
    # Generate random private key
    private_key = secrets.token_bytes(32)
    
    # Create signer (derives public key)
    signer = ED25519Signer(private_key)
    public_key = signer.public_key
    
    # Save keys securely
    save_private_key(node_id, private_key)
    save_public_key(node_id, public_key)
    
    print(f"✓ Generated keys for node: {node_id}")
    print(f"  Public key: {public_key.hex()}")
    print(f"  Private key: [REDACTED]")
    
    return private_key, public_key

# Usage
private_key, public_key = generate_node_keys("node_001")
```

### Key Storage

#### Private Key Storage (CRITICAL)

```python
import os
from pathlib import Path
import json

def save_private_key(node_id: str, private_key: bytes):
    """
    Save private key with restricted permissions
    
    SECURITY: Private keys must be protected!
    - File permissions: 0600 (owner read/write only)
    - Encrypted at rest (optional but recommended)
    - Never commit to version control
    - Never log or print
    """
    
    key_dir = Path(".diotec360_keys")
    key_dir.mkdir(mode=0o700, exist_ok=True)
    
    key_file = key_dir / f"{node_id}.private.key"
    
    # Write with restricted permissions
    with open(key_file, 'wb') as f:
        f.write(private_key)
    
    # Set file permissions (Unix/Linux/macOS)
    if os.name != 'nt':  # Not Windows
        os.chmod(key_file, 0o600)
    
    print(f"✓ Private key saved: {key_file}")
    print(f"  Permissions: 0600 (owner only)")

def load_private_key(node_id: str) -> bytes:
    """Load private key from secure storage"""
    key_file = Path(".diotec360_keys") / f"{node_id}.private.key"
    
    if not key_file.exists():
        raise FileNotFoundError(f"Private key not found: {key_file}")
    
    # Verify permissions (Unix/Linux/macOS)
    if os.name != 'nt':
        stat_info = key_file.stat()
        mode = stat_info.st_mode & 0o777
        if mode != 0o600:
            raise PermissionError(f"Insecure permissions on {key_file}: {oct(mode)}")
    
    with open(key_file, 'rb') as f:
        return f.read()
```

#### Public Key Storage

```python
def save_public_key(node_id: str, public_key: bytes):
    """Save public key (can be shared)"""
    key_dir = Path(".diotec360_keys")
    key_dir.mkdir(exist_ok=True)
    
    key_file = key_dir / f"{node_id}.public.key"
    
    with open(key_file, 'wb') as f:
        f.write(public_key)
    
    print(f"✓ Public key saved: {key_file}")

def load_public_key(node_id: str) -> bytes:
    """Load public key"""
    key_file = Path(".diotec360_keys") / f"{node_id}.public.key"
    
    with open(key_file, 'rb') as f:
        return f.read()
```

---

## Key Distribution

### Public Key Registry

```python
class PublicKeyRegistry:
    """
    Central registry of node public keys
    
    This registry is shared among all nodes in the network.
    It maps node IDs to their public keys.
    """
    
    def __init__(self, registry_file: str = ".diotec360_keys/registry.json"):
        self.registry_file = Path(registry_file)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Load registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                data = json.load(f)
                # Convert hex strings back to bytes
                return {k: bytes.fromhex(v) for k, v in data.items()}
        return {}
    
    def _save_registry(self):
        """Save registry to file"""
        # Convert bytes to hex strings for JSON
        data = {k: v.hex() for k, v in self.registry.items()}
        
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_node(self, node_id: str, public_key: bytes):
        """Register a node's public key"""
        if node_id in self.registry:
            if self.registry[node_id] != public_key:
                raise ValueError(f"Node {node_id} already registered with different key")
        
        self.registry[node_id] = public_key
        self._save_registry()
        print(f"✓ Registered node: {node_id}")
    
    def get_public_key(self, node_id: str) -> bytes:
        """Get a node's public key"""
        if node_id not in self.registry:
            raise KeyError(f"Node {node_id} not registered")
        
        return self.registry[node_id]
    
    def list_nodes(self) -> list:
        """List all registered nodes"""
        return list(self.registry.keys())

# Usage
registry = PublicKeyRegistry()
registry.register_node("node_001", public_key)
```

### Distributing Public Keys

#### Method 1: Manual Distribution

```bash
# Copy public key to other nodes
scp .diotec360_keys/node_001.public.key user@node2:/path/to/diotec360/.diotec360_keys/
scp .diotec360_keys/node_001.public.key user@node3:/path/to/diotec360/.diotec360_keys/
```

#### Method 2: Registry File Distribution

```bash
# Share registry file with all nodes
scp .diotec360_keys/registry.json user@node2:/path/to/diotec360/.diotec360_keys/
scp .diotec360_keys/registry.json user@node3:/path/to/diotec360/.diotec360_keys/
```

#### Method 3: Automated Distribution (Advanced)

```python
def distribute_public_keys(nodes: list):
    """Automatically distribute public keys to all nodes"""
    registry = PublicKeyRegistry()
    
    for node in nodes:
        # SSH to node and copy registry
        import subprocess
        subprocess.run([
            "scp",
            ".diotec360_keys/registry.json",
            f"{node['user']}@{node['host']}:{node['path']}/.diotec360_keys/"
        ])
        
        print(f"✓ Distributed keys to {node['host']}")

# Usage
nodes = [
    {"user": "admin", "host": "node2.example.com", "path": "/opt/diotec360"},
    {"user": "admin", "host": "node3.example.com", "path": "/opt/diotec360"},
]
distribute_public_keys(nodes)
```

---

## Key Rotation

### When to Rotate Keys

Rotate keys when:

1. **Scheduled Rotation**: Every 90-365 days (policy dependent)
2. **Compromise Suspected**: Immediately
3. **Employee Departure**: Within 24 hours
4. **Security Audit**: As recommended
5. **Cryptographic Weakness**: If ED25519 is compromised (unlikely)

### Rotation Procedure

```python
def rotate_node_keys(node_id: str):
    """
    Rotate keys for a node
    
    Process:
    1. Generate new key pair
    2. Backup old keys
    3. Update registry
    4. Distribute new public key
    5. Restart node with new keys
    """
    
    print(f"=== Key Rotation for {node_id} ===\n")
    
    # Step 1: Backup old keys
    old_private = load_private_key(node_id)
    old_public = load_public_key(node_id)
    
    backup_dir = Path(".diotec360_keys/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_private = backup_dir / f"{node_id}.private.{timestamp}.key"
    backup_public = backup_dir / f"{node_id}.public.{timestamp}.key"
    
    with open(backup_private, 'wb') as f:
        f.write(old_private)
    with open(backup_public, 'wb') as f:
        f.write(old_public)
    
    print(f"✓ Backed up old keys")
    
    # Step 2: Generate new keys
    new_private, new_public = generate_node_keys(node_id)
    
    # Step 3: Update registry
    registry = PublicKeyRegistry()
    registry.register_node(node_id, new_public)
    
    print(f"✓ Updated registry")
    
    # Step 4: Distribute new public key
    print(f"\n⚠ ACTION REQUIRED:")
    print(f"  1. Distribute new registry to all nodes")
    print(f"  2. Restart node {node_id} with new keys")
    print(f"  3. Verify gossip messages are signed correctly")
    
    return new_private, new_public

# Usage
rotate_node_keys("node_001")
```

### Zero-Downtime Rotation (Advanced)

```python
def zero_downtime_rotation(node_id: str):
    """
    Rotate keys with zero downtime
    
    Process:
    1. Generate new key pair
    2. Node accepts messages signed with BOTH old and new keys
    3. Node starts signing with new key
    4. After grace period, remove old key
    """
    
    # Step 1: Generate new key
    new_private, new_public = generate_node_keys(f"{node_id}_new")
    
    # Step 2: Add new key to registry (keep old key)
    registry = PublicKeyRegistry()
    registry.register_node(f"{node_id}_new", new_public)
    
    # Step 3: Configure node to accept both keys
    # (Implementation depends on gossip protocol)
    
    # Step 4: Wait for grace period (e.g., 24 hours)
    print("⚠ Grace period: 24 hours")
    print("  All nodes must update to new registry")
    
    # Step 5: Remove old key after grace period
    # (Manual step after verification)
```

---

## Security Best Practices

### 1. Private Key Protection

**DO**:
- ✓ Store private keys with 0600 permissions
- ✓ Encrypt private keys at rest (optional)
- ✓ Use hardware security modules (HSM) for production
- ✓ Backup private keys to secure offline storage
- ✓ Use separate keys for each node

**DON'T**:
- ✗ Commit private keys to version control
- ✗ Log or print private keys
- ✗ Share private keys between nodes
- ✗ Store private keys in plaintext on shared storage
- ✗ Email or chat private keys

### 2. Key Generation

```python
# ✓ GOOD: Use cryptographically secure random
import secrets
private_key = secrets.token_bytes(32)

# ✗ BAD: Don't use weak random
import random
private_key = bytes([random.randint(0, 255) for _ in range(32)])  # INSECURE!
```

### 3. Key Storage

```python
# ✓ GOOD: Restricted permissions
os.chmod(key_file, 0o600)

# ✗ BAD: World-readable
os.chmod(key_file, 0o644)  # INSECURE!
```

### 4. Key Distribution

```python
# ✓ GOOD: Secure channel (SSH, TLS)
subprocess.run(["scp", key_file, "user@host:/secure/path/"])

# ✗ BAD: Insecure channel
subprocess.run(["ftp", key_file, "host"])  # INSECURE!
```

### 5. Key Backup

```python
# ✓ GOOD: Encrypted offline backup
backup_keys_encrypted(private_key, passphrase="strong_passphrase")

# ✗ BAD: Plaintext backup on network storage
shutil.copy(key_file, "/network/share/backup/")  # INSECURE!
```

---

## Monitoring and Auditing

### Key Usage Monitoring

```python
def monitor_key_usage():
    """Monitor key usage for anomalies"""
    
    # Track signature verifications
    metrics = {
        "signatures_verified": 0,
        "signatures_failed": 0,
        "unknown_nodes": set(),
    }
    
    # Alert on anomalies
    if metrics["signatures_failed"] > 10:
        send_alert("High signature failure rate")
    
    if len(metrics["unknown_nodes"]) > 0:
        send_alert(f"Unknown nodes detected: {metrics['unknown_nodes']}")
```

### Audit Log

```python
def log_key_event(event_type: str, node_id: str, details: dict):
    """Log key management events for audit"""
    
    import logging
    
    logger = logging.getLogger("key_management")
    logger.info(f"{event_type}: {node_id} - {details}")
    
    # Events to log:
    # - KEY_GENERATED
    # - KEY_ROTATED
    # - KEY_COMPROMISED
    # - KEY_REVOKED
    # - SIGNATURE_FAILED
    # - UNKNOWN_NODE
```

---

## Incident Response

### Compromised Private Key

If a private key is compromised:

1. **Immediate Actions** (within 1 hour):
   ```python
   # Revoke compromised key
   revoke_node_key("node_001", reason="compromised")
   
   # Generate new key
   new_private, new_public = generate_node_keys("node_001")
   
   # Update registry
   registry.register_node("node_001", new_public)
   
   # Distribute new registry
   distribute_public_keys(all_nodes)
   ```

2. **Investigation** (within 24 hours):
   - Review access logs
   - Identify how key was compromised
   - Check for unauthorized messages
   - Assess damage

3. **Remediation** (within 7 days):
   - Fix security vulnerability
   - Rotate all keys (precaution)
   - Update security procedures
   - Train staff

### Unknown Node Detection

If an unknown node is detected:

```python
def handle_unknown_node(node_id: str, public_key: bytes):
    """Handle detection of unknown node"""
    
    # Log the event
    log_key_event("UNKNOWN_NODE", node_id, {
        "public_key": public_key.hex(),
        "timestamp": time.time(),
    })
    
    # Alert security team
    send_alert(f"Unknown node detected: {node_id}")
    
    # Reject all messages from this node
    # (Automatic in Sovereign Gossip)
    
    # Investigate:
    # - Is this a new legitimate node?
    # - Is this an attack?
    # - Should we add to registry?
```

---

## Troubleshooting

### Q: Signature verification failing

**A**: Check:
1. Public key in registry matches node's actual public key
2. Node is using correct private key
3. Message format is correct
4. Clock skew (timestamps)

### Q: Node can't load private key

**A**: Check:
1. File exists: `.diotec360_keys/node_001.private.key`
2. File permissions: `0600`
3. File is not corrupted
4. Process has read permissions

### Q: How to recover lost private key?

**A**: You can't. Generate new key pair and update registry. This is why backups are critical.

### Q: Can I use the same key for multiple nodes?

**A**: NO. Each node must have its own unique key pair. Sharing keys compromises security and makes it impossible to identify which node sent a message.

---

## Support

For key management assistance:

1. Review this guide
2. Check security logs
3. Verify key file permissions
4. Contact security team
5. Escalate to development if needed

---

*"Every message is signed. Every signature is verified. No exceptions."*  
— RVC v2 Hardening Security Principle
