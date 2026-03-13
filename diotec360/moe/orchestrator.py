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
MOEOrchestrator - Central Coordination for MOE Intelligence Layer

Central coordinator that manages expert lifecycle, routes intents to appropriate
experts, executes experts in parallel, and aggregates results into unified verdicts.

Key Responsibilities:
- Expert registration and management
- Feature extraction from transaction intents
- Parallel expert execution using ThreadPoolExecutor
- Result aggregation via consensus engine
- Telemetry recording for monitoring

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .base_expert import BaseExpert
from .data_models import ExpertVerdict, MOEResult
from .gating_network import GatingNetwork
from .consensus_engine import ConsensusEngine
from .telemetry import ExpertTelemetry


@dataclass
class CacheEntry:
    """
    Cache entry for verdict caching.
    
    Attributes:
        result: Cached MOEResult
        timestamp: Unix timestamp when cached
        cache_key: SHA256 hash of intent
    """
    result: MOEResult
    timestamp: float
    cache_key: str


class MOEOrchestrator:
    """
    Central coordinator for MOE Intelligence Layer.
    
    Manages the complete verification workflow:
    1. Extract features from transaction intent
    2. Route to appropriate experts via gating network
    3. Execute experts in parallel
    4. Aggregate results via consensus engine
    5. Record telemetry for monitoring
    
    Attributes:
        experts: Dictionary of registered experts (name -> BaseExpert)
        gating_network: Intelligent routing system
        consensus_engine: Verdict aggregation system
        telemetry: Performance tracking system
    """
    
    def __init__(
        self,
        max_workers: int = 3,
        expert_timeout: int = 30,
        telemetry_db_path: str = ".aethel_moe/telemetry.db",
        cache_ttl_seconds: int = 300,
        enable_cache: bool = True
    ):
        """
        Initialize MOE Orchestrator.
        
        Args:
            max_workers: Maximum number of parallel expert threads (default 3)
            expert_timeout: Timeout for expert execution in seconds (default 30)
            telemetry_db_path: Path to telemetry database
            cache_ttl_seconds: Time-to-live for cache entries in seconds (default 300 = 5 minutes)
            enable_cache: Enable verdict caching (default True)
        """
        self.experts: Dict[str, BaseExpert] = {}
        self.gating_network = GatingNetwork()
        self.consensus_engine = ConsensusEngine()
        self.telemetry = ExpertTelemetry(telemetry_db_path)
        
        # Execution configuration
        self.max_workers = max_workers
        self.expert_timeout = expert_timeout
        
        # Verdict caching
        self.enable_cache = enable_cache
        self.cache_ttl_seconds = cache_ttl_seconds
        self.verdict_cache: Dict[str, CacheEntry] = {}
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Statistics
        self.total_verifications = 0
        self.total_latency_ms = 0.0
        
    def register_expert(self, expert: BaseExpert) -> None:
        """
        Register a new expert with the orchestrator.
        
        Args:
            expert: BaseExpert instance to register
            
        Raises:
            ValueError: If expert with same name already registered
        """
        if expert.name in self.experts:
            raise ValueError(f"Expert '{expert.name}' is already registered")
        
        self.experts[expert.name] = expert
        
    def unregister_expert(self, expert_name: str) -> None:
        """
        Unregister an expert from the orchestrator.
        
        Args:
            expert_name: Name of expert to unregister
            
        Raises:
            KeyError: If expert not found
        """
        if expert_name not in self.experts:
            raise KeyError(f"Expert '{expert_name}' not found")
        
        del self.experts[expert_name]
        
    def verify_transaction(self, intent: str, tx_id: str) -> MOEResult:
        """
        Main verification entry point.
        
        Workflow:
        1. Check cache for existing verdict
        2. Extract features from intent
        3. Route to appropriate experts via gating network
        4. Execute experts in parallel
        5. Aggregate results via consensus engine
        6. Record telemetry and update cache
        
        Args:
            intent: Transaction intent string to verify
            tx_id: Unique transaction identifier
            
        Returns:
            MOEResult with consensus verdict and expert verdicts
        """
        start_time = time.time()
        
        try:
            # Step 1: Check cache
            if self.enable_cache:
                cached_result = self._check_cache(intent)
                if cached_result is not None:
                    # Cache hit - return cached result
                    self.cache_hits += 1
                    self.total_verifications += 1
                    
                    # Update transaction ID to current one
                    cached_result.transaction_id = tx_id
                    
                    return cached_result
                
                # Cache miss
                self.cache_misses += 1
            
            # Step 2: Extract features from intent
            features = self._extract_features(intent)
            
            # Step 3: Determine which experts to activate
            expert_names = self.gating_network.route(intent)
            
            # Validate that requested experts are registered
            available_experts = [name for name in expert_names if name in self.experts]
            
            # If no experts from gating network are available, use all registered experts
            if not available_experts and self.experts:
                available_experts = list(self.experts.keys())
            
            if not available_experts:
                # No experts available - return rejection
                return MOEResult(
                    transaction_id=tx_id,
                    consensus="REJECTED",
                    overall_confidence=0.0,
                    expert_verdicts=[],
                    total_latency_ms=(time.time() - start_time) * 1000,
                    activated_experts=[]
                )
            
            # Step 4: Execute experts in parallel
            verdicts = self._execute_experts_parallel(available_experts, intent, tx_id)
            
            # Step 5: Reach consensus
            consensus = self.consensus_engine.aggregate(verdicts)
            
            # Update consensus with correct transaction ID
            consensus.transaction_id = tx_id
            
            # Calculate total latency
            total_latency_ms = (time.time() - start_time) * 1000
            consensus.total_latency_ms = total_latency_ms
            
            # Step 6: Record telemetry
            self.telemetry.record(tx_id, verdicts, consensus)
            
            # Update cache
            if self.enable_cache:
                self._update_cache(intent, consensus)
            
            # Update statistics
            self.total_verifications += 1
            self.total_latency_ms += total_latency_ms
            
            return consensus
            
        except Exception as e:
            # Orchestrator failure - return rejection
            latency_ms = (time.time() - start_time) * 1000
            
            return MOEResult(
                transaction_id=tx_id,
                consensus="REJECTED",
                overall_confidence=0.0,
                expert_verdicts=[
                    ExpertVerdict(
                        expert_name="MOE_Orchestrator",
                        verdict="REJECT",
                        confidence=0.0,
                        latency_ms=latency_ms,
                        reason=f"Orchestrator failure: {str(e)}",
                        proof_trace={'error': str(e), 'error_type': type(e).__name__}
                    )
                ],
                total_latency_ms=latency_ms,
                activated_experts=[]
            )
    
    def _extract_features(self, intent: str) -> Dict[str, Any]:
        """
        Extract features from transaction intent.
        
        Delegates to gating network for feature extraction.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Dictionary of extracted features
        """
        return self.gating_network.extract_features(intent)
    
    def _execute_experts_parallel(
        self,
        expert_names: List[str],
        intent: str,
        tx_id: str
    ) -> List[ExpertVerdict]:
        """
        Execute multiple experts in parallel using ThreadPoolExecutor.
        
        Args:
            expert_names: List of expert names to execute
            intent: Transaction intent string
            tx_id: Transaction identifier
            
        Returns:
            List of expert verdicts
        """
        verdicts = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all expert verification tasks
            futures = {
                executor.submit(self.experts[name].verify, intent, tx_id): name
                for name in expert_names
            }
            
            # Collect results as they complete (without global timeout on as_completed)
            for future in as_completed(futures):
                expert_name = futures[future]
                
                try:
                    # Get verdict with timeout
                    verdict = future.result(timeout=self.expert_timeout)
                    verdicts.append(verdict)
                    
                except FuturesTimeoutError:
                    # Expert timed out - create timeout verdict
                    verdicts.append(ExpertVerdict(
                        expert_name=expert_name,
                        verdict="REJECT",
                        confidence=0.0,
                        latency_ms=self.expert_timeout * 1000,
                        reason=f"Expert timeout ({self.expert_timeout}s)",
                        proof_trace={'timeout': True}
                    ))
                    
                except Exception as e:
                    # Expert crashed - create error verdict
                    verdicts.append(ExpertVerdict(
                        expert_name=expert_name,
                        verdict="REJECT",
                        confidence=0.0,
                        latency_ms=0.0,
                        reason=f"Expert failure: {str(e)}",
                        proof_trace={'error': str(e), 'error_type': type(e).__name__}
                    ))
        
        return verdicts
    
    def get_expert_status(self) -> Dict[str, Any]:
        """
        Return current status of all registered experts.
        
        Returns:
            Dictionary with expert status information:
            - registered_experts: List of expert names
            - expert_stats: Statistics per expert
            - orchestrator_stats: Overall orchestrator statistics
        """
        expert_stats = {}
        for name, expert in self.experts.items():
            expert_stats[name] = expert.get_stats()
        
        orchestrator_stats = {
            'total_verifications': self.total_verifications,
            'average_latency_ms': (
                self.total_latency_ms / self.total_verifications
                if self.total_verifications > 0 else 0.0
            ),
            'max_workers': self.max_workers,
            'expert_timeout': self.expert_timeout
        }
        
        return {
            'registered_experts': list(self.experts.keys()),
            'expert_stats': expert_stats,
            'orchestrator_stats': orchestrator_stats,
            'gating_network_stats': self.gating_network.get_routing_stats(),
            'consensus_engine_config': self.consensus_engine.get_config()
        }
    
    def get_telemetry_stats(self, time_window_seconds: int = 3600) -> Dict[str, Any]:
        """
        Get telemetry statistics for all experts.
        
        Args:
            time_window_seconds: Time window for statistics (default 1 hour)
            
        Returns:
            Dictionary with telemetry statistics
        """
        return {
            'experts': self.telemetry.get_all_experts_stats(time_window_seconds),
            'time_window_seconds': time_window_seconds
        }
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        return self.telemetry.export_prometheus()
    
    def reset_statistics(self) -> None:
        """
        Reset orchestrator statistics (for testing).
        """
        self.total_verifications = 0
        self.total_latency_ms = 0.0
    
    def _generate_cache_key(self, intent: str) -> str:
        """
        Generate cache key from intent using SHA256 hash.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(intent.encode('utf-8')).hexdigest()
    
    def _check_cache(self, intent: str) -> Optional[MOEResult]:
        """
        Check cache for existing verdict.
        
        Args:
            intent: Transaction intent string
            
        Returns:
            Cached MOEResult if found and not expired, None otherwise
        """
        cache_key = self._generate_cache_key(intent)
        
        if cache_key not in self.verdict_cache:
            return None
        
        entry = self.verdict_cache[cache_key]
        
        # Check if entry has expired
        age_seconds = time.time() - entry.timestamp
        if age_seconds > self.cache_ttl_seconds:
            # Expired - remove from cache
            del self.verdict_cache[cache_key]
            return None
        
        # Valid cache entry
        return entry.result
    
    def _update_cache(self, intent: str, result: MOEResult) -> None:
        """
        Update cache with new verdict.
        
        Args:
            intent: Transaction intent string
            result: MOEResult to cache
        """
        cache_key = self._generate_cache_key(intent)
        
        entry = CacheEntry(
            result=result,
            timestamp=time.time(),
            cache_key=cache_key
        )
        
        self.verdict_cache[cache_key] = entry
    
    def clear_cache(self) -> int:
        """
        Clear all cached verdicts.
        
        Returns:
            Number of entries cleared
        """
        count = len(self.verdict_cache)
        self.verdict_cache.clear()
        return count
    
    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        for cache_key, entry in self.verdict_cache.items():
            age_seconds = current_time - entry.timestamp
            if age_seconds > self.cache_ttl_seconds:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.verdict_cache[key]
        
        return len(expired_keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics:
            - enabled: Whether caching is enabled
            - ttl_seconds: Cache TTL in seconds
            - size: Current number of cached entries
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_rate: Cache hit rate (0.0-1.0)
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'enabled': self.enable_cache,
            'ttl_seconds': self.cache_ttl_seconds,
            'size': len(self.verdict_cache),
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate
        }
    
    def set_cache_enabled(self, enabled: bool) -> None:
        """
        Enable or disable verdict caching.
        
        Args:
            enabled: True to enable caching, False to disable
        """
        self.enable_cache = enabled
        
        if not enabled:
            # Clear cache when disabling
            self.clear_cache()
    
    def set_cache_ttl(self, ttl_seconds: int) -> None:
        """
        Set cache TTL (time-to-live).
        
        Args:
            ttl_seconds: TTL in seconds
            
        Raises:
            ValueError: If TTL is negative
        """
        if ttl_seconds < 0:
            raise ValueError("Cache TTL must be non-negative")
        
        self.cache_ttl_seconds = ttl_seconds

