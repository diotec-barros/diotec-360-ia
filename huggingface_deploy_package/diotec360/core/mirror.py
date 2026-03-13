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
Aethel Mirror - The Reality Manifestation Engine

This module creates instant previews of verified code.
No build. No deploy. Just pure logic streaming.

"The app exists the moment the proof completes."
"""

import uuid
import time
from typing import Dict, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class Manifestation:
    """
    A manifested reality - an app running without deployment.
    """
    manifest_id: str
    bundle_hash: str
    verified_code: str
    wasm_binary: Optional[bytes]
    status: str  # 'LIVE', 'EXPIRED', 'ARCHIVED'
    created_at: float
    access_count: int
    merkle_root: str


class AethelMirror:
    """
    The Mirror doesn't deploy apps - it manifests them.
    
    Traditional: Write → Build → Deploy → Wait → Access
    Mirror: Prove → Manifest → Access (instant)
    
    The secret: Since the code is proved, we can stream
    the WASM binary directly to the browser. No server needed.
    """
    
    def __init__(self):
        self.active_previews: Dict[str, Manifestation] = {}
        self.max_preview_age = 3600  # 1 hour
        
    def create_instant_manifestation(
        self, 
        bundle_hash: str, 
        verified_code: str,
        wasm_binary: Optional[bytes] = None
    ) -> str:
        """
        Creates an instant preview ID.
        
        No build needed. No deploy needed.
        Pure logic served via stream.
        
        Args:
            bundle_hash: Hash of the verified bundle
            verified_code: The proved Aethel code
            wasm_binary: Optional pre-compiled WASM
            
        Returns:
            URL to access the manifestation
        """
        
        # Generate unique manifest ID
        manifest_id = self._generate_manifest_id(bundle_hash)
        
        # Compute Merkle root for this manifestation
        merkle_root = self._compute_merkle_root(verified_code)
        
        # Store the manifestation in memory (or Redis in production)
        manifestation = Manifestation(
            manifest_id=manifest_id,
            bundle_hash=bundle_hash,
            verified_code=verified_code,
            wasm_binary=wasm_binary,
            status='LIVE',
            created_at=time.time(),
            access_count=0,
            merkle_root=merkle_root
        )
        
        self.active_previews[manifest_id] = manifestation
        
        # Return instant preview URL
        return f"/preview/{manifest_id}"
    
    def get_manifestation(self, manifest_id: str) -> Optional[Manifestation]:
        """
        Retrieves a manifestation by ID.
        
        If expired, returns None.
        """
        manifestation = self.active_previews.get(manifest_id)
        
        if not manifestation:
            return None
        
        # Check if expired
        age = time.time() - manifestation.created_at
        if age > self.max_preview_age:
            manifestation.status = 'EXPIRED'
            return None
        
        # Increment access count
        manifestation.access_count += 1
        
        return manifestation
    
    def stream_manifestation(self, manifest_id: str) -> Optional[Dict]:
        """
        Streams a manifestation to the browser.
        
        Returns the data needed to render the app instantly.
        """
        manifestation = self.get_manifestation(manifest_id)
        
        if not manifestation:
            return None
        
        return {
            'manifest_id': manifestation.manifest_id,
            'code': manifestation.verified_code,
            'wasm': manifestation.wasm_binary.hex() if manifestation.wasm_binary else None,
            'merkle_root': manifestation.merkle_root,
            'status': manifestation.status,
            'created_at': manifestation.created_at,
            'access_count': manifestation.access_count
        }
    
    def publish_to_vercel(
        self, 
        manifest_id: str,
        vercel_token: Optional[str] = None
    ) -> Optional[str]:
        """
        Publishes a manifestation to Vercel for permanent hosting.
        
        This is optional - user can keep using the instant preview
        or publish for a permanent URL.
        
        Args:
            manifest_id: The manifestation to publish
            vercel_token: Vercel API token (optional)
            
        Returns:
            Vercel deployment URL or None
        """
        manifestation = self.get_manifestation(manifest_id)
        
        if not manifestation:
            return None
        
        # TODO: Implement Vercel API integration
        # For now, return a placeholder
        return f"https://{manifest_id}.vercel.app"
    
    def cleanup_expired(self):
        """
        Removes expired manifestations from memory.
        """
        current_time = time.time()
        expired_ids = []
        
        for manifest_id, manifestation in self.active_previews.items():
            age = current_time - manifestation.created_at
            if age > self.max_preview_age:
                expired_ids.append(manifest_id)
        
        for manifest_id in expired_ids:
            del self.active_previews[manifest_id]
        
        return len(expired_ids)
    
    def get_stats(self) -> Dict:
        """
        Returns statistics about active manifestations.
        """
        total = len(self.active_previews)
        live = sum(1 for m in self.active_previews.values() if m.status == 'LIVE')
        total_accesses = sum(m.access_count for m in self.active_previews.values())
        
        return {
            'total_manifestations': total,
            'live_manifestations': live,
            'total_accesses': total_accesses,
            'avg_accesses': total_accesses / total if total > 0 else 0
        }
    
    def _generate_manifest_id(self, bundle_hash: str) -> str:
        """
        Generates a unique manifest ID.
        
        Format: First 8 chars of hash + timestamp suffix
        """
        timestamp = str(int(time.time() * 1000))[-6:]
        return f"{bundle_hash[:8]}-{timestamp}"
    
    def _compute_merkle_root(self, code: str) -> str:
        """
        Computes Merkle root for the manifestation.
        """
        return hashlib.sha256(code.encode()).hexdigest()


# Singleton instance
_mirror = None

def get_mirror() -> AethelMirror:
    """Get the global Mirror instance"""
    global _mirror
    if _mirror is None:
        _mirror = AethelMirror()
    return _mirror
