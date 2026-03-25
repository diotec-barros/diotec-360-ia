"""
DIOTEC 360 IA - Geo Oracle Service v10.0.9

IP Geolocation service with intelligent caching
Resolves peer IP addresses to geographic coordinates

"Where Silicon Meets Geography"
"""

import requests
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GeoOracle:
    """
    IP Geolocation service with 24-hour caching
    
    Primary API: ip-api.com (free tier: 45 req/min)
    Fallback API: ipapi.co (free tier: 1000 req/day)
    
    Features:
    - Automatic caching (24h TTL)
    - Dual API fallback
    - City-level accuracy
    - Privacy-preserving (approximate location only)
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(hours=24)
        self.request_count = 0
    
    def resolve(self, ip_address: str) -> Optional[Dict]:
        """
        Resolve IP address to geographic coordinates
        
        Args:
            ip_address: IPv4 or IPv6 address
        
        Returns:
            {
                'city': 'Luanda',
                'country': 'Angola',
                'country_code': 'AO',
                'lat': -8.8383,
                'lon': 13.2344,
                'continent': 'Africa'
            }
            
            Returns None if resolution fails
        """
        
        # Check cache first
        if ip_address in self.cache:
            cached = self.cache[ip_address]
            age = datetime.now() - cached['timestamp']
            
            if age < self.cache_ttl:
                logger.debug(f"Cache hit for {ip_address} (age: {age})")
                return cached['location']
            else:
                # Cache expired
                logger.debug(f"Cache expired for {ip_address}")
                del self.cache[ip_address]
        
        # Try primary API (ip-api.com)
        location = self._resolve_primary(ip_address)
        
        if location:
            self._cache_location(ip_address, location)
            return location
        
        # Fallback to secondary API (ipapi.co)
        location = self._resolve_fallback(ip_address)
        
        if location:
            self._cache_location(ip_address, location)
            return location
        
        logger.error(f"Failed to resolve IP: {ip_address}")
        return None
    
    def _resolve_primary(self, ip_address: str) -> Optional[Dict]:
        """Resolve using ip-api.com (primary)"""
        try:
            self.request_count += 1
            
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                params={'fields': 'status,country,countryCode,city,lat,lon,continent'},
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"Primary API returned {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get('status') != 'success':
                logger.warning(f"Primary API failed: {data.get('message', 'Unknown error')}")
                return None
            
            location = {
                'city': data.get('city', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'country_code': data.get('countryCode', 'XX'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'continent': data.get('continent', 'Unknown')
            }
            
            logger.info(f"Resolved {ip_address} → {location['city']}, {location['country']}")
            return location
            
        except requests.Timeout:
            logger.warning(f"Primary API timeout for {ip_address}")
            return None
        except Exception as e:
            logger.error(f"Primary API error: {e}")
            return None
    
    def _resolve_fallback(self, ip_address: str) -> Optional[Dict]:
        """Resolve using ipapi.co (fallback)"""
        try:
            self.request_count += 1
            
            response = requests.get(
                f'https://ipapi.co/{ip_address}/json/',
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"Fallback API returned {response.status_code}")
                return None
            
            data = response.json()
            
            # Check for error response
            if 'error' in data:
                logger.warning(f"Fallback API error: {data['error']}")
                return None
            
            location = {
                'city': data.get('city', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', 'XX'),
                'lat': data.get('latitude', 0),
                'lon': data.get('longitude', 0),
                'continent': data.get('continent_code', 'Unknown')
            }
            
            logger.info(f"Resolved {ip_address} → {location['city']}, {location['country']} (fallback)")
            return location
            
        except requests.Timeout:
            logger.warning(f"Fallback API timeout for {ip_address}")
            return None
        except Exception as e:
            logger.error(f"Fallback API error: {e}")
            return None
    
    def _cache_location(self, ip_address: str, location: Dict):
        """Cache location data"""
        self.cache[ip_address] = {
            'location': location,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cached location for {ip_address}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'request_count': self.request_count,
            'cache_hit_rate': len(self.cache) / max(self.request_count, 1)
        }

# Global instance
geo_oracle = GeoOracle()

