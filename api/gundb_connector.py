"""
DIOTEC 360 IA - GunDB Python Connector v10.0.9

WebSocket client for connecting Python backend to GunDB P2P network
Enables real-time data synchronization via Gossip Protocol

"Where Python Meets the Mesh"
"""

import asyncio
import websockets
import json
import logging
from typing import Callable, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GunDBConnector:
    """
    Python client for GunDB network
    
    Connects to GunDB relay server via WebSocket
    Publishes peer announcements and proof events
    Subscribes to network state changes
    
    Features:
    - WebSocket connection to relay
    - Auto-reconnect on disconnect
    - Message routing to callbacks
    - Heartbeat monitoring
    """
    
    def __init__(self, relay_url: str = "wss://gun-relay.diotec360.com/gun"):
        self.relay_url = relay_url
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.subscriptions: Dict[str, Callable] = {}
        self.is_connected = False
        self.reconnect_delay = 5  # seconds
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._listen_task: Optional[asyncio.Task] = None
        self._send_task: Optional[asyncio.Task] = None
    
    async def connect(self):
        """
        Connect to GunDB relay server
        
        Establishes WebSocket connection and starts message processing
        Auto-reconnects on disconnect
        """
        while True:
            try:
                logger.info(f"Connecting to GunDB relay: {self.relay_url}")
                
                self.ws = await websockets.connect(
                    self.relay_url,
                    ping_interval=20,
                    ping_timeout=10
                )
                
                self.is_connected = True
                logger.info("✅ Connected to GunDB relay")
                
                # Start message processing tasks
                self._listen_task = asyncio.create_task(self._listen())
                self._send_task = asyncio.create_task(self._send_queue())
                
                # Wait for disconnect
                await self._listen_task
                
            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                self.is_connected = False
                
            except Exception as e:
                logger.error(f"Connection error: {e}", exc_info=True)
                self.is_connected = False
            
            # Reconnect after delay
            logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
            await asyncio.sleep(self.reconnect_delay)
    
    async def _listen(self):
        """Listen for incoming GunDB messages"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._route_message(data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.is_connected = False
            
        except Exception as e:
            logger.error(f"Listen error: {e}", exc_info=True)
            self.is_connected = False
    
    async def _send_queue(self):
        """Process outgoing message queue"""
        while True:
            try:
                message = await self.message_queue.get()
                
                if self.ws and self.is_connected:
                    await self.ws.send(json.dumps(message))
                    logger.debug(f"Sent message: {message.get('put', {}).keys()}")
                else:
                    logger.warning("Cannot send message: not connected")
                    
            except Exception as e:
                logger.error(f"Send error: {e}", exc_info=True)
    
    async def _route_message(self, data: Dict):
        """
        Route incoming message to subscriptions
        
        GunDB message format:
        {
            "put": {
                "path/to/data": { ... }
            },
            "get": {
                "#": "path/to/data"
            }
        }
        """
        
        # Handle PUT messages (data updates)
        if 'put' in data:
            for path, value in data['put'].items():
                # Find matching subscriptions
                for sub_path, callback in self.subscriptions.items():
                    if path.startswith(sub_path):
                        try:
                            # Call subscription callback
                            if asyncio.iscoroutinefunction(callback):
                                await callback(path, value)
                            else:
                                callback(path, value)
                                
                        except Exception as e:
                            logger.error(f"Subscription callback error: {e}", exc_info=True)
        
        # Handle GET responses
        elif 'get' in data:
            logger.debug(f"Received GET response: {data['get']}")
    
    async def put(self, path: str, data: Dict):
        """
        Publish data to GunDB
        
        Args:
            path: GunDB path (e.g., 'lattice/peers/abc123')
            data: Data to publish
        
        Example:
            await gun.put('lattice/peers/server_id', {
                'peer_id': 'server_id',
                'status': 'connected',
                'last_seen': time.time()
            })
        """
        message = {
            'put': {
                path: {
                    **data,
                    '_': {
                        '#': path,
                        '>': {
                            k: int(datetime.now().timestamp() * 1000)
                            for k in data.keys()
                        }
                    }
                }
            }
        }
        
        await self.message_queue.put(message)
        logger.debug(f"Queued PUT: {path}")
    
    def on(self, path: str, callback: Callable):
        """
        Subscribe to GunDB path
        
        Args:
            path: GunDB path to subscribe to
            callback: Function to call on updates (sync or async)
        
        Example:
            gun.on('lattice/peers', lambda path, data: print(data))
        """
        self.subscriptions[path] = callback
        
        # Send subscription request
        message = {
            'get': {
                '#': path
            }
        }
        
        asyncio.create_task(self.message_queue.put(message))
        logger.info(f"Subscribed to: {path}")
    
    async def get(self, path: str) -> Optional[Dict]:
        """
        Get data from GunDB (one-time fetch)
        
        Args:
            path: GunDB path to fetch
        
        Returns:
            Data at path or None
        """
        # TODO: Implement one-time fetch with response handling
        # For now, use subscriptions
        logger.warning("get() not fully implemented, use on() for subscriptions")
        return None
    
    async def disconnect(self):
        """Gracefully disconnect from GunDB"""
        logger.info("Disconnecting from GunDB...")
        
        self.is_connected = False
        
        # Cancel tasks
        if self._listen_task:
            self._listen_task.cancel()
        if self._send_task:
            self._send_task.cancel()
        
        # Close WebSocket
        if self.ws:
            await self.ws.close()
        
        logger.info("Disconnected from GunDB")
    
    def get_status(self) -> Dict:
        """Get connection status"""
        return {
            'connected': self.is_connected,
            'relay_url': self.relay_url,
            'subscriptions': len(self.subscriptions),
            'queue_size': self.message_queue.qsize()
        }

# Global instance (initialized on startup)
gun: Optional[GunDBConnector] = None

def get_gun() -> GunDBConnector:
    """Get global GunDB connector instance"""
    global gun
    if gun is None:
        raise RuntimeError("GunDB connector not initialized")
    return gun

async def initialize_gun(relay_url: str = "wss://gun-relay.diotec360.com/gun"):
    """Initialize global GunDB connector"""
    global gun
    gun = GunDBConnector(relay_url)
    
    # Start connection in background
    asyncio.create_task(gun.connect())
    
    # Wait for initial connection
    for _ in range(10):
        if gun.is_connected:
            break
        await asyncio.sleep(0.5)
    
    if not gun.is_connected:
        logger.warning("GunDB connection not established yet (will retry in background)")
    
    return gun

