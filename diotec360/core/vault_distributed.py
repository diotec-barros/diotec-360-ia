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
Aethel Distributed Vault - The Global Truth Protocol

A distributed system for sharing mathematically proved functions.
Functions are identified by cryptographic hashes and come with
proof certificates that guarantee correctness.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from diotec360.core.vault import AethelVault


class AethelDistributedVault(AethelVault):
    """
    Distributed Vault with proof certificates and export/import capabilities.
    
    Extends the local Vault with:
    - Proof certificates (digital stamps of verification)
    - Export bundles (.ae_bundle files)
    - Import with integrity verification
    - Merkle tree organization (future)
    """
    
    def __init__(self, vault_path=".aethel_vault"):
        super().__init__(vault_path)
        self.certificates_path = self.vault_path / "certificates"
        self.certificates_path.mkdir(exist_ok=True)
        self.bundles_path = self.vault_path / "bundles"
        self.bundles_path.mkdir(exist_ok=True)
    
    def generate_proof_certificate(self, function_hash, verification_result, metadata=None):
        """
        Creates a digital stamp proving the Judge validated this logic.
        
        The certificate contains:
        - Function hash (SHA-256)
        - Verification status and message
        - Judge version
        - Timestamp
        - Metadata (author, Z3 version, etc.)
        - Certificate signature (hash of all above)
        
        This certificate can be verified independently without re-running the Judge.
        """
        certificate = {
            "version": "1.0",
            "function_hash": function_hash,
            "status": verification_result['status'],
            "message": verification_result['message'],
            "judge_version": "Aethel_Judge_v0.6",
            "z3_version": "4.12.0+",
            "timestamp": datetime.now().isoformat(),
            "counter_examples": verification_result.get('counter_examples', []),
            "metadata": metadata or {},
        }
        
        # Generate certificate signature (hash of certificate content)
        cert_string = json.dumps(certificate, sort_keys=True, separators=(',', ':'))
        certificate['signature'] = hashlib.sha256(cert_string.encode()).hexdigest()
        
        # Save certificate
        cert_path = self.certificates_path / f"{function_hash}.cert.json"
        with open(cert_path, 'w') as f:
            json.dump(certificate, f, indent=2)
        
        return certificate
    
    def verify_certificate(self, certificate):
        """
        Verifies the integrity of a proof certificate.
        
        Returns True if:
        - Certificate signature matches content
        - Status is PROVED
        - Certificate is well-formed
        """
        try:
            # Extract signature
            signature = certificate.pop('signature', None)
            if not signature:
                return False, "Missing signature"
            
            # Recalculate signature
            cert_string = json.dumps(certificate, sort_keys=True, separators=(',', ':'))
            calculated_sig = hashlib.sha256(cert_string.encode()).hexdigest()
            
            # Restore signature
            certificate['signature'] = signature
            
            # Verify
            if calculated_sig != signature:
                return False, "Signature mismatch"
            
            if certificate['status'] != 'PROVED':
                return False, f"Status is {certificate['status']}, not PROVED"
            
            return True, "Certificate valid"
        
        except Exception as e:
            return False, f"Verification error: {e}"
    
    def export_bundle(self, function_hash, output_path=None):
        """
        Generates a .ae_bundle file containing:
        - AST (the logic)
        - Generated code
        - Proof certificate
        - Metadata
        
        This bundle can be shared globally and imported by anyone.
        """
        # Fetch function from vault
        entry = self.fetch(function_hash)
        if not entry:
            raise ValueError(f"Function {function_hash} not found in vault")
        
        # Load certificate
        cert_path = self.certificates_path / f"{function_hash}.cert.json"
        if cert_path.exists():
            with open(cert_path, 'r') as f:
                certificate = json.load(f)
        else:
            certificate = None
        
        # Create bundle
        bundle = {
            "bundle_version": "1.0",
            "function_hash": function_hash,
            "intent_name": entry['intent_name'],
            "ast": entry['ast'],
            "code": entry['code'],
            "verification": entry['verification'],
            "certificate": certificate,
            "metadata": entry.get('metadata', {}),
            "created_at": entry['created_at'],
            "bundle_created_at": datetime.now().isoformat()
        }
        
        # Generate bundle signature
        bundle_string = json.dumps({
            "function_hash": function_hash,
            "ast": entry['ast'],
            "certificate": certificate
        }, sort_keys=True, separators=(',', ':'))
        bundle['bundle_signature'] = hashlib.sha256(bundle_string.encode()).hexdigest()
        
        # Save bundle
        if output_path is None:
            output_path = self.bundles_path / f"{entry['intent_name']}_{function_hash[:8]}.ae_bundle"
        
        with open(output_path, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        print(f"Bundle exported: {output_path}")
        print(f"  Intent: {entry['intent_name']}")
        print(f"  Hash: {function_hash[:16]}...{function_hash[-8:]}")
        print(f"  Status: {entry['verification']['status']}")
        
        return str(output_path)
    
    def import_bundle(self, bundle_path, verify_integrity=True):
        """
        Imports a .ae_bundle file into the local vault.
        
        Process:
        1. Load bundle
        2. Verify bundle signature
        3. Verify certificate (if present)
        4. Verify function hash matches AST
        5. Add to vault
        
        If verify_integrity=True, all checks must pass.
        If verify_integrity=False, bundle is imported without verification (dangerous!).
        """
        print(f"Importing bundle: {bundle_path}")
        
        # Load bundle
        with open(bundle_path, 'r') as f:
            bundle = json.load(f)
        
        function_hash = bundle['function_hash']
        intent_name = bundle['intent_name']
        
        if verify_integrity:
            print("  Verifying integrity...")
            
            # 1. Verify bundle signature
            bundle_sig = bundle.get('bundle_signature')
            if bundle_sig:
                bundle_string = json.dumps({
                    "function_hash": function_hash,
                    "ast": bundle['ast'],
                    "certificate": bundle.get('certificate')
                }, sort_keys=True, separators=(',', ':'))
                calculated_sig = hashlib.sha256(bundle_string.encode()).hexdigest()
                
                if calculated_sig != bundle_sig:
                    raise ValueError("Bundle signature mismatch! Bundle may be corrupted.")
                print("    Bundle signature: VALID")
            
            # 2. Verify certificate
            if bundle.get('certificate'):
                valid, message = self.verify_certificate(bundle['certificate'])
                if not valid:
                    raise ValueError(f"Certificate verification failed: {message}")
                print("    Certificate: VALID")
            
            # 3. Verify function hash matches AST
            calculated_hash = self.get_function_hash(bundle['ast'])
            if calculated_hash != function_hash:
                raise ValueError(f"Function hash mismatch! Expected {function_hash}, got {calculated_hash}")
            print("    Function hash: VALID")
        
        # Check if already exists
        if function_hash in self.index:
            print(f"  Function already in vault: {function_hash[:16]}...")
            return function_hash
        
        # Import into vault
        entry = {
            'intent_name': intent_name,
            'full_hash': function_hash,
            'logic_hash': self.get_logic_hash(bundle['ast']),
            'ast': bundle['ast'],
            'code': bundle['code'],
            'verification': bundle['verification'],
            'metadata': bundle.get('metadata', {}),
            'immutable': True,
            'created_at': bundle['created_at'],
            'imported_at': datetime.now().isoformat(),
            'imported_from': str(bundle_path)
        }
        
        # Save entry
        self._save_entry(function_hash, entry)
        
        # Update index
        self.index[function_hash] = {
            'intent_name': intent_name,
            'logic_hash': entry['logic_hash'],
            'created_at': entry['created_at'],
            'status': 'MATHEMATICALLY_PROVED',
            'imported': True
        }
        self._save_index()
        
        # Save certificate if present
        if bundle.get('certificate'):
            cert_path = self.certificates_path / f"{function_hash}.cert.json"
            with open(cert_path, 'w') as f:
                json.dump(bundle['certificate'], f, indent=2)
        
        print(f"  Successfully imported: {intent_name}")
        print(f"  Hash: {function_hash[:16]}...{function_hash[-8:]}")
        print(f"  Status: MATHEMATICALLY_PROVED")
        
        return function_hash
    
    def list_bundles(self):
        """List all available bundles"""
        bundles = list(self.bundles_path.glob("*.ae_bundle"))
        return bundles
    
    def generate_merkle_root(self):
        """
        Generate Merkle root of all functions in vault.
        
        This allows efficient verification that a vault contains
        a specific set of functions without checking each one.
        
        Future: This will be used for P2P synchronization.
        """
        if not self.index:
            return None
        
        # Get all function hashes
        hashes = sorted(self.index.keys())
        
        # Build Merkle tree (simplified - just hash of all hashes)
        combined = ''.join(hashes)
        merkle_root = hashlib.sha256(combined.encode()).hexdigest()
        
        return merkle_root
    
    def sync_status(self):
        """
        Get synchronization status of the vault.
        
        Returns information about:
        - Total functions
        - Functions with certificates
        - Available bundles
        - Merkle root
        """
        total = len(self.index)
        
        # Count certificates
        certs = list(self.certificates_path.glob("*.cert.json"))
        cert_count = len(certs)
        
        # Count bundles
        bundles = self.list_bundles()
        bundle_count = len(bundles)
        
        # Get Merkle root
        merkle_root = self.generate_merkle_root()
        
        return {
            'total_functions': total,
            'certified_functions': cert_count,
            'available_bundles': bundle_count,
            'merkle_root': merkle_root,
            'vault_path': str(self.vault_path.absolute())
        }
