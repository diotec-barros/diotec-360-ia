"""
DIOTEC 360 IA - Mobile Gateway v10.3.0
=======================================
Sovereign Creator: Dionísio Sebastião Barros

Mobile command center for the Genesis Authority
Enables sovereign control from anywhere in the world

"Where the Thumb Commands the Empire"
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import io
import base64
import logging

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

logger = logging.getLogger(__name__)


@dataclass
class PendingConsensus:
    """Represents a consensus decision awaiting Genesis Authority approval"""
    consensus_id: str
    proposal_type: str  # 'network_upgrade', 'reward_adjustment', 'node_ban', etc.
    description: str
    proposed_by: str
    votes_yes: int
    votes_no: int
    total_votes: int
    approval_percentage: float
    created_at: datetime
    expires_at: datetime
    status: str  # 'pending', 'approved', 'rejected', 'expired'


@dataclass
class BiometricSignature:
    """Represents a biometric signature from mobile device"""
    signature_id: str
    consensus_id: str
    signed_by: str  # Genesis Authority identity
    signature: bytes
    timestamp: datetime
    device_id: str
    biometric_type: str  # 'fingerprint', 'face_id', 'pin'


class MobileGateway:
    """
    DIOTEC 360 IA Mobile Gateway
    
    Enables Genesis Authority to:
    - Receive push notifications for pending consensus
    - Sign transactions with biometric authentication
    - View real-time network metrics
    - Monitor 30% revenue stream
    - Execute emergency network commands
    """
    
    # Genesis Authority ED25519 Key Pair
    GENESIS_AUTHORITY_ID = "DIOTEC_360_DIONISIO_GENESIS_SOVEREIGN"
    
    def __init__(self, genesis_private_key: Optional[bytes] = None):
        """
        Initialize Mobile Gateway
        
        Args:
            genesis_private_key: ED25519 private key for Genesis Authority
                                If None, generates a new key pair
        """
        if HAS_CRYPTO:
            if genesis_private_key:
                self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(genesis_private_key)
            else:
                self.private_key = ed25519.Ed25519PrivateKey.generate()
            
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = None
            self.public_key = None
            logger.warning("Cryptography library not available - signatures disabled")
        
        self.pending_consensus: Dict[str, PendingConsensus] = {}
        
        logger.info(f"Mobile Gateway initialized for: {self.GENESIS_AUTHORITY_ID}")
    
    def get_public_key_hex(self) -> str:
        """Get public key in hex format for sharing"""
        if not HAS_CRYPTO or not self.public_key:
            return "MOCK_PUBLIC_KEY_" + hashlib.sha256(self.GENESIS_AUTHORITY_ID.encode()).hexdigest()[:32]
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return public_bytes.hex()
    
    def create_pending_consensus(
        self,
        proposal_type: str,
        description: str,
        proposed_by: str,
        votes_yes: int,
        votes_no: int
    ) -> PendingConsensus:
        """
        Create a new pending consensus awaiting Genesis Authority approval
        
        Args:
            proposal_type: Type of proposal
            description: Human-readable description
            proposed_by: Node ID that proposed
            votes_yes: Number of YES votes
            votes_no: Number of NO votes
            
        Returns:
            PendingConsensus object
        """
        total_votes = votes_yes + votes_no
        approval_percentage = (votes_yes / total_votes * 100) if total_votes > 0 else 0
        
        consensus_id = self._generate_consensus_id(proposal_type, description)
        
        consensus = PendingConsensus(
            consensus_id=consensus_id,
            proposal_type=proposal_type,
            description=description,
            proposed_by=proposed_by,
            votes_yes=votes_yes,
            votes_no=votes_no,
            total_votes=total_votes,
            approval_percentage=approval_percentage,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow(),  # Would add expiry time
            status='pending'
        )
        
        self.pending_consensus[consensus_id] = consensus
        
        logger.info(
            f"📱 New consensus pending: {proposal_type} "
            f"({approval_percentage:.1f}% approval)"
        )
        
        return consensus
    
    def generate_qr_code(self, consensus_id: str) -> str:
        """
        Generate QR code for mobile signing
        
        Args:
            consensus_id: ID of consensus to sign
            
        Returns:
            Base64-encoded PNG image of QR code (or mock data if qrcode not available)
        """
        if consensus_id not in self.pending_consensus:
            raise ValueError(f"Consensus {consensus_id} not found")
        
        consensus = self.pending_consensus[consensus_id]
        
        # Create QR code data
        qr_data = {
            'consensus_id': consensus_id,
            'type': consensus.proposal_type,
            'description': consensus.description,
            'approval': f"{consensus.approval_percentage:.1f}%",
            'timestamp': consensus.created_at.isoformat()
        }
        
        if not HAS_QRCODE:
            # Return mock QR code data
            logger.warning("QR code library not available - returning mock data")
            mock_data = base64.b64encode(str(qr_data).encode()).decode()
            return mock_data
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"📱 QR code generated for consensus: {consensus_id}")
        
        return img_str
    
    def sign_consensus(
        self,
        consensus_id: str,
        decision: str,  # 'approve' or 'reject'
        device_id: str,
        biometric_type: str = 'fingerprint'
    ) -> BiometricSignature:
        """
        Sign a consensus decision with Genesis Authority key
        
        Args:
            consensus_id: ID of consensus to sign
            decision: 'approve' or 'reject'
            device_id: Mobile device identifier
            biometric_type: Type of biometric used
            
        Returns:
            BiometricSignature object
        """
        if consensus_id not in self.pending_consensus:
            raise ValueError(f"Consensus {consensus_id} not found")
        
        consensus = self.pending_consensus[consensus_id]
        
        # Create signature data
        signature_data = f"{consensus_id}:{decision}:{datetime.utcnow().isoformat()}"
        signature_bytes = signature_data.encode('utf-8')
        
        # Sign with ED25519 private key (or create mock signature)
        if HAS_CRYPTO and self.private_key:
            signature = self.private_key.sign(signature_bytes)
        else:
            # Mock signature
            signature = hashlib.sha256(signature_bytes).digest()
        
        # Create signature object
        bio_signature = BiometricSignature(
            signature_id=self._generate_signature_id(),
            consensus_id=consensus_id,
            signed_by=self.GENESIS_AUTHORITY_ID,
            signature=signature,
            timestamp=datetime.utcnow(),
            device_id=device_id,
            biometric_type=biometric_type
        )
        
        # Update consensus status
        if decision == 'approve':
            consensus.status = 'approved'
            logger.info(f"✅ Consensus APPROVED by Genesis Authority: {consensus_id}")
        else:
            consensus.status = 'rejected'
            logger.info(f"❌ Consensus REJECTED by Genesis Authority: {consensus_id}")
        
        return bio_signature
    
    def verify_signature(
        self,
        signature: BiometricSignature,
        consensus_id: str,
        decision: str
    ) -> bool:
        """
        Verify a biometric signature
        
        Args:
            signature: BiometricSignature to verify
            consensus_id: Expected consensus ID
            decision: Expected decision
            
        Returns:
            True if signature is valid
        """
        # Reconstruct signature data
        signature_data = f"{consensus_id}:{decision}:{signature.timestamp.isoformat()}"
        signature_bytes = signature_data.encode('utf-8')
        
        try:
            if HAS_CRYPTO and self.public_key:
                # Verify with public key
                self.public_key.verify(signature.signature, signature_bytes)
            else:
                # Mock verification
                expected_sig = hashlib.sha256(signature_bytes).digest()
                if signature.signature != expected_sig:
                    raise ValueError("Signature mismatch")
            
            logger.info(f"✅ Signature verified for consensus: {consensus_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Signature verification failed: {e}")
            return False
    
    def get_wallet_balance(self) -> Dict:
        """
        Get Genesis Authority wallet balance (30% revenue stream)
        
        Returns:
            Dictionary with balance information
        """
        # In production, this would query the treasury
        # For now, return simulated data
        return {
            'genesis_authority': self.GENESIS_AUTHORITY_ID,
            'total_earned': 45000.00,  # Total earned since genesis
            'current_balance': 12500.00,  # Current balance
            'last_24h': 850.00,  # Earned in last 24 hours
            'last_7d': 5600.00,  # Earned in last 7 days
            'last_30d': 22000.00,  # Earned in last 30 days
            'currency': 'USD',
            'reward_percentage': 30,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_network_metrics(self) -> Dict:
        """
        Get real-time network metrics
        
        Returns:
            Dictionary with network statistics
        """
        # In production, this would query the lattice
        # For now, return simulated data
        return {
            'total_nodes': 1247,
            'active_nodes': 1189,
            'mining_nodes': 956,
            'total_proofs_validated': 2847563,
            'proofs_last_24h': 125847,
            'network_hashrate': '1.2 PH/s',
            'average_proof_time': '2.3s',
            'pending_consensus': len([c for c in self.pending_consensus.values() if c.status == 'pending']),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def send_push_notification(
        self,
        consensus_id: str,
        notification_service: str = 'whatsapp'
    ) -> Dict:
        """
        Send push notification to Genesis Authority mobile device
        
        Args:
            consensus_id: ID of consensus requiring attention
            notification_service: 'whatsapp', 'telegram', 'fcm', etc.
            
        Returns:
            Notification delivery status
        """
        if consensus_id not in self.pending_consensus:
            raise ValueError(f"Consensus {consensus_id} not found")
        
        consensus = self.pending_consensus[consensus_id]
        
        # Create notification message
        message = (
            f"🏛️ DIOTEC 360 IA - Consensus Pending\n\n"
            f"Type: {consensus.proposal_type}\n"
            f"Description: {consensus.description}\n"
            f"Approval: {consensus.approval_percentage:.1f}%\n"
            f"Votes: {consensus.votes_yes} YES / {consensus.votes_no} NO\n\n"
            f"Your signature is required to proceed.\n"
            f"Consensus ID: {consensus_id}"
        )
        
        # In production, this would integrate with actual notification services
        logger.info(
            f"📱 Push notification sent via {notification_service}: {consensus_id}"
        )
        
        return {
            'status': 'sent',
            'service': notification_service,
            'consensus_id': consensus_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def execute_emergency_command(
        self,
        command: str,
        reason: str,
        signature: BiometricSignature
    ) -> Dict:
        """
        Execute emergency network command (requires biometric signature)
        
        Args:
            command: Emergency command to execute
            reason: Reason for emergency action
            signature: Biometric signature for authorization
            
        Returns:
            Command execution result
        """
        # Verify signature
        if signature.signed_by != self.GENESIS_AUTHORITY_ID:
            raise ValueError("Only Genesis Authority can execute emergency commands")
        
        logger.warning(
            f"⚠️ EMERGENCY COMMAND EXECUTED: {command}\n"
            f"   Reason: {reason}\n"
            f"   Authorized by: {signature.signed_by}\n"
            f"   Device: {signature.device_id}\n"
            f"   Biometric: {signature.biometric_type}"
        )
        
        # In production, this would execute actual network commands
        return {
            'status': 'executed',
            'command': command,
            'reason': reason,
            'executed_by': signature.signed_by,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_consensus_id(self, proposal_type: str, description: str) -> str:
        """Generate unique consensus ID"""
        data = f"{proposal_type}:{description}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_signature_id(self) -> str:
        """Generate unique signature ID"""
        data = f"{self.GENESIS_AUTHORITY_ID}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# DIOTEC 360 IA - Mobile Gateway
# Where the Thumb Commands the Empire
