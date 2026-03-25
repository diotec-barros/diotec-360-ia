"""
DIOTEC 360 IA - Peer Announcer Service v10.0.9

Announces backend server as a peer in the Lattice P2P network
Sends heartbeat every 10 seconds to maintain presence
Broadcasts proof verification events to network

"Where the Server Becomes a Peer"
"""

import asyncio
import time
import socket
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

from api.gundb_connector import get_gun
from api.geo_oracle import geo_oracle

logger = logging.getLogger(__name__)

class PeerAnnouncer:
    """
    Announces backend server as a peer in Lattice network
    
    Features:
    - Automatic peer announcement on startup
    - Heartbeat every 10 seconds
    - IP geolocation integration
    - Proof event broadcasting
    - Graceful shutdown
    """
    
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        self.is_running = False
        self.start_time = time.time()
        self.proofs_validated = 0
        self.ip_address: Optional[str] = None
        self.location: Optional[Dict] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """
        Start announcing peer presence
        
        Steps:
        1. Get server's public IP
        2. Resolve IP to geographic location
        3. Announce to GunDB network
        4. Start heartbeat loop
        """
        logger.info(f"Starting peer announcer for: {self.peer_id}")
        
        self.is_running = True
        
        # Get public IP
        self.ip_address = await self._get_public_ip()
        logger.info(f"Public IP: {self.ip_address}")
        
        # Resolve location
        if self.ip_address and self.ip_address != '127.0.0.1':
            self.location = geo_oracle.resolve(self.ip_address)
            if self.location:
                logger.info(
                    f"Location: {self.location['city']}, {self.location['country']}"
                )
        
        # Fallback location if resolution fails
        if not self.location:
            logger.warning("Using fallback location (Unknown)")
            self.location = {
                'city': 'Unknown',
                'country': 'Unknown',
                'country_code': 'XX',
                'lat': 0,
                'lon': 0,
                'continent': 'Unknown'
            }
        
        # Initial announcement
        await self._announce()
        
        # Start heartbeat loop
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("✅ Peer announcer started")
    
    async def stop(self):
        """Stop announcing and send goodbye message"""
        logger.info("Stopping peer announcer...")
        
        self.is_running = False
        
        # Cancel heartbeat task
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Send goodbye message
        try:
            gun = get_gun()
            await gun.put(f'lattice/peers/{self.peer_id}', {
                'peer_id': self.peer_id,
                'status': 'offline',
                'last_seen': int(time.time() * 1000)
            })
            logger.info("Sent goodbye message")
        except Exception as e:
            logger.error(f"Error sending goodbye: {e}")
        
        logger.info("Peer announcer stopped")
    
    async def _heartbeat_loop(self):
        """Send heartbeat every 10 seconds"""
        while self.is_running:
            try:
                await asyncio.sleep(10)
                await self._announce()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", exc_info=True)
    
    async def _announce(self):
        """Send peer announcement to GunDB"""
        try:
            gun = get_gun()
            
            peer_data = {
                'peer_id': self.peer_id,
                'ip_address': self.ip_address or '127.0.0.1',
                'location': self.location,
                'status': 'connected',
                'uptime_seconds': int(time.time() - self.start_time),
                'proofs_validated': self.proofs_validated,
                'last_seen': int(time.time() * 1000),
                'heartbeat_interval': 10000
            }
            
            await gun.put(f'lattice/peers/{self.peer_id}', peer_data)
            
            logger.debug(
                f"Heartbeat sent: {self.peer_id} "
                f"(uptime: {peer_data['uptime_seconds']}s, proofs: {self.proofs_validated})"
            )
            
        except Exception as e:
            logger.error(f"Error announcing peer: {e}", exc_info=True)
    
    async def _get_public_ip(self) -> str:
        """
        Get server's public IP address
        
        Returns:
            Public IP address or '127.0.0.1' if detection fails
        """
        try:
            # Try ipify.org
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Failed to get IP from ipify: {e}")
        
        try:
            # Try icanhazip.com
            response = requests.get('https://icanhazip.com', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Failed to get IP from icanhazip: {e}")
        
        # Fallback to localhost
        logger.warning("Could not detect public IP, using 127.0.0.1")
        return '127.0.0.1'
    
    async def broadcast_proof_event(
        self,
        event_type: str,
        message: str,
        source_peer_id: str,
        destination_peer_id: Optional[str] = None,
        credits_earned: Optional[int] = None
    ):
        """
        Broadcast proof verification event to network
        
        Args:
            event_type: Type of event ('proof_validated', 'merkle_sync', etc.)
            message: Human-readable message
            source_peer_id: Peer that triggered the event
            destination_peer_id: Destination peer (optional)
            credits_earned: Credits earned from proof (optional)
        """
        try:
            gun = get_gun()
            
            event_id = f"evt_{int(time.time() * 1000)}_{source_peer_id[:8]}"
            
            event_data = {
                'event_id': event_id,
                'type': event_type,
                'message': message,
                'source_peer_id': source_peer_id,
                'timestamp': int(time.time() * 1000)
            }
            
            if destination_peer_id:
                event_data['destination_peer_id'] = destination_peer_id
            
            if credits_earned is not None:
                event_data['credits_earned'] = credits_earned
            
            await gun.put(f'lattice/events/{event_id}', event_data)
            
            logger.info(f"📢 Broadcasted event: {message}")
            
            # Increment proof counter if it's a proof validation
            if event_type == 'proof_validated':
                self.proofs_validated += 1
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}", exc_info=True)
    
    def get_status(self) -> Dict:
        """Get announcer status"""
        return {
            'peer_id': self.peer_id,
            'is_running': self.is_running,
            'ip_address': self.ip_address,
            'location': self.location,
            'uptime_seconds': int(time.time() - self.start_time),
            'proofs_validated': self.proofs_validated
        }

# Global instance
peer_announcer: Optional[PeerAnnouncer] = None

def get_peer_announcer() -> PeerAnnouncer:
    """Get global peer announcer instance"""
    global peer_announcer
    if peer_announcer is None:
        raise RuntimeError("Peer announcer not initialized")
    return peer_announcer

async def initialize_peer_announcer(peer_id: str):
    """Initialize and start global peer announcer"""
    global peer_announcer
    peer_announcer = PeerAnnouncer(peer_id)
    await peer_announcer.start()
    return peer_announcer

