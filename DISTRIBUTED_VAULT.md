# Aethel Distributed Vault - The Global Truth Protocol

## Overview

The Aethel Distributed Vault extends the local vault with cryptographic proof certificates and bundle export/import capabilities. This enables global sharing of mathematically verified functions without requiring recipients to re-run the Judge.

## Architecture

### Components

1. **Proof Certificates** - Digital stamps proving the Judge validated the logic
2. **Export Bundles** - Portable `.ae_bundle` files containing code + certificate
3. **Import Verification** - Multi-layer integrity checking before accepting bundles
4. **Merkle Trees** - Efficient vault state verification (future P2P sync)

### File Structure

```
.DIOTEC360_vault/
├── index.json                          # Function registry
├── {hash}.json                         # Function entries
├── certificates/
│   └── {hash}.cert.json               # Proof certificates
└── bundles/
    └── {name}_{hash}.ae_bundle        # Exportable bundles
```

## Proof Certificates

### What is a Certificate?

A certificate is a cryptographically signed document proving that the Aethel Judge verified a function's logic. It contains:

- Function hash (SHA-256)
- Verification status (PROVED/FAILED)
- Judge version and Z3 version
- Timestamp
- Counter-examples (if any)
- Certificate signature (hash of all above)

### Certificate Format

```json
{
  "version": "1.0",
  "function_hash": "9ad9e80d616d938a7bb8527f66f8c9a94796ea6e6d6d6c4cab9e564747042f1d",
  "status": "PROVED",
  "message": "Code is mathematically safe. All post-conditions guaranteed.",
  "judge_version": "DIOTEC360_Judge_v0.6",
  "z3_version": "4.12.0+",
  "timestamp": "2026-02-01T23:56:28.496230",
  "counter_examples": [],
  "metadata": {
    "ai_provider": "anthropic",
    "attempts": 1
  },
  "signature": "a7f3c9e2..."
}
```

### Certificate Generation

Certificates are automatically generated during compilation:

```python
from DIOTEC360_kernel import AethelKernel

kernel = AethelKernel()
result = kernel.compile(source_code)

# Certificate is automatically created and stored
# in .DIOTEC360_vault/certificates/{hash}.cert.json
```

## Export Bundles

### What is a Bundle?

A bundle is a self-contained package that includes:

- AST (the logic)
- Generated code
- Proof certificate
- Verification result
- Metadata
- Bundle signature

### Bundle Format

```json
{
  "bundle_version": "1.0",
  "function_hash": "9ad9e80d...",
  "intent_name": "check_balance",
  "ast": { ... },
  "code": "fn check_balance(...) { ... }",
  "verification": {
    "status": "PROVED",
    "message": "..."
  },
  "certificate": { ... },
  "metadata": { ... },
  "bundle_signature": "c5f43004..."
}
```

### Exporting Functions

```bash
# Export a specific function
Diotec360 vault export <function-hash>

# Export with custom output path
Diotec360 vault export <function-hash> -o my_function.ae_bundle
```

Example:
```bash
Diotec360 vault export 9ad9e80d616d938a7bb8527f66f8c9a94796ea6e6d6d6c4cab9e564747042f1d
```

## Import Verification

### Security Model

When importing a bundle, the system performs multi-layer verification:

1. **Bundle Signature** - Verifies bundle hasn't been tampered with
2. **Certificate Validation** - Checks certificate signature and status
3. **Hash Verification** - Ensures function hash matches AST
4. **Status Check** - Confirms function is PROVED

### Importing Bundles

```bash
# Import with full verification (recommended)
Diotec360 vault import bundle.ae_bundle

# Import without verification (dangerous!)
Diotec360 vault import bundle.ae_bundle --no-verify
```

### Import Process

```
┌─────────────────┐
│  Load Bundle    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Bundle   │
│   Signature     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Proof    │
│  Certificate    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Function │
│      Hash       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Add to Vault    │
└─────────────────┘
```

## Vault Synchronization

### Sync Status

Check the current state of your vault:

```bash
Diotec360 vault sync
```

Output:
```
[VAULT] Synchronization Status:
  Total Functions: 5
  Certified Functions: 5
  Available Bundles: 5
  Merkle Root: 6b606a7957d904d0...
  Vault Path: /path/to/.DIOTEC360_vault
```

### Merkle Root

The Merkle root is a single hash representing the entire vault state. It enables:

- Efficient verification that two vaults contain the same functions
- Quick detection of missing or modified functions
- Future P2P synchronization protocol

## CLI Commands

### List Functions

```bash
Diotec360 vault list
```

Shows all functions in the vault with their hashes and status.

### Show Statistics

```bash
Diotec360 vault stats
```

Displays:
- Total functions
- Proved functions
- Storage used
- Vault path

### Export Function

```bash
Diotec360 vault export <hash> [-o output.ae_bundle]
```

Creates a portable bundle file.

### Import Bundle

```bash
Diotec360 vault import <bundle-file> [--no-verify]
```

Imports a bundle into the local vault.

### Sync Status

```bash
Diotec360 vault sync
```

Shows synchronization status and Merkle root.

## Use Cases

### 1. Sharing Verified Libraries

Developer A creates a secure payment function:

```bash
# Compile and verify
aethel build payment.ae

# Export bundle
Diotec360 vault export <hash> -o payment_secure.ae_bundle

# Share bundle with team
```

Developer B imports and uses it:

```bash
# Import with verification
Diotec360 vault import payment_secure.ae_bundle

# Function is now available in local vault
Diotec360 vault list
```

### 2. Building Trust Networks

Organizations can share their vault's Merkle root to prove they're using verified code:

```bash
# Organization publishes their Merkle root
Diotec360 vault sync
# Merkle Root: 6b606a7957d904d0...

# Others can verify they have the same functions
# by comparing Merkle roots
```

### 3. Audit Trail

Every bundle contains:
- Who verified it (Judge version)
- When it was verified (timestamp)
- How many attempts it took (metadata)
- The exact logic that was proved (AST)

This creates an immutable audit trail for compliance.

## Security Considerations

### Trust Model

- **Certificates are NOT cryptographic signatures** - They prove the Judge verified the logic, but don't prove WHO ran the Judge
- **Bundle signatures prevent tampering** - But don't prove authorship
- **Hash verification ensures integrity** - The function hash is deterministic based on AST

### Future Enhancements (Epoch 2+)

1. **Digital Signatures** - Sign bundles with private keys to prove authorship
2. **Web of Trust** - Build reputation networks for bundle sources
3. **P2P Synchronization** - Automatic vault syncing across networks
4. **Blockchain Anchoring** - Publish Merkle roots to blockchain for timestamping

## API Usage

### Python API

```python
from aethel.core.vault_distributed import AethelDistributedVault

# Initialize vault
vault = AethelDistributedVault()

# Export bundle
bundle_path = vault.export_bundle(function_hash)

# Import bundle
imported_hash = vault.import_bundle(
    bundle_path,
    verify_integrity=True
)

# Check sync status
status = vault.sync_status()
print(f"Total: {status['total_functions']}")
print(f"Certified: {status['certified_functions']}")
print(f"Merkle Root: {status['merkle_root']}")
```

### Certificate Verification

```python
import json

# Load certificate
with open('.DIOTEC360_vault/certificates/{hash}.cert.json') as f:
    cert = json.load(f)

# Verify certificate
valid, message = vault.verify_certificate(cert)
if valid:
    print("Certificate is valid!")
else:
    print(f"Certificate invalid: {message}")
```

## Roadmap

### v0.7 (Current)
- ✅ Proof certificates
- ✅ Bundle export/import
- ✅ Integrity verification
- ✅ Merkle root generation

### v0.8 (Next)
- 🔄 Digital signatures for bundles
- 🔄 Author identity verification
- 🔄 Bundle metadata enrichment

### v1.0 (Future)
- 📋 P2P vault synchronization
- 📋 Blockchain anchoring
- 📋 Web of trust network
- 📋 Decentralized bundle registry

## Conclusion

The Distributed Vault transforms Aethel from a local compiler into a global truth protocol. Functions verified once can be shared globally, creating a network of mathematically guaranteed code.

This is the foundation for:
- **Trustless code sharing** - No need to trust the sender, trust the math
- **Immutable audit trails** - Every function has a provable history
- **Global code libraries** - Verified functions anyone can use
- **The end of "works on my machine"** - If it's proved, it works everywhere

---

**Status**: Epoch 1 - The Great Expansion  
**Version**: Diotec360 v0.7  
**Last Updated**: 2026-02-01
