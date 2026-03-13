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

import asyncio
import inspect
import json
import os
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from diotec360.core.persistence import AethelPersistenceLayer
from diotec360.nexo.p2p_node import sync_state_if_empty
from diotec360.core.env_compat import getbool, getenv


@dataclass
class LatticeP2PConfig:
    enabled: bool
    listen_multiaddrs: List[str]
    bootstrap_peers: List[str]
    topic: str

    @classmethod
    def from_env(cls) -> "LatticeP2PConfig":
        enabled = getbool("DIOTEC360_P2P_ENABLED", legacy="AETHEL_P2P_ENABLED", default=False)

        listen = (getenv("DIOTEC360_P2P_LISTEN", legacy="AETHEL_P2P_LISTEN", default="") or "").strip()
        listen_multiaddrs = [s.strip() for s in listen.split(",") if s.strip()] if listen else []

        bootstrap = (getenv("DIOTEC360_P2P_BOOTSTRAP", legacy="AETHEL_P2P_BOOTSTRAP", default="") or "").strip()
        bootstrap_peers = [s.strip() for s in bootstrap.split(",") if s.strip()] if bootstrap else []

        topic = (getenv("DIOTEC360_P2P_TOPIC", legacy="AETHEL_P2P_TOPIC", default="aethel/lattice/v1") or "aethel/lattice/v1").strip() or "aethel/lattice/v1"

        return cls(
            enabled=enabled,
            listen_multiaddrs=listen_multiaddrs,
            bootstrap_peers=bootstrap_peers,
            topic=topic,
        )


class LatticeStreams:
    def __init__(self, config: LatticeP2PConfig, persistence: AethelPersistenceLayer):
        self.config = config
        self.persistence = persistence
        self._started = False
        self._libp2p_available = False
        self._start_error: Optional[str] = None

        self.peer_id: Optional[str] = None
        self.listen_addrs: List[str] = []

        self._host = None
        self._pubsub = None
        self._sub_task: Optional[asyncio.Task] = None

        self._trio_thread: Optional[threading.Thread] = None
        self._trio_stop: Optional[threading.Event] = None
        self._trio_token: Any = None
        self._rx_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        
        # CRITICAL FIX (RVC3-003): Add heartbeat tracking infrastructure
        self._peer_heartbeats: Dict[str, float] = {}  # peer_id -> last_heartbeat_timestamp

    @property
    def started(self) -> bool:
        return self._started

    @property
    def libp2p_available(self) -> bool:
        return self._libp2p_available

    @property
    def start_error(self) -> Optional[str]:
        return self._start_error

    async def start(self) -> Tuple[bool, str]:
        if not self.config.enabled:
            return False, "p2p_disabled"

        if self._started:
            return True, "already_started"

        try:
            import trio  # type: ignore
            from libp2p import new_host  # type: ignore
            from libp2p.pubsub.gossipsub import (  # type: ignore
                GossipSub,
                PROTOCOL_ID,
                PROTOCOL_ID_V11,
                PROTOCOL_ID_V12,
            )
            from libp2p.pubsub.pubsub import Pubsub  # type: ignore
            from libp2p.peer.peerinfo import info_from_p2p_addr  # type: ignore
            from libp2p.peer.peerstore import PERMANENT_ADDR_TTL  # type: ignore
            from multiaddr import Multiaddr  # type: ignore
        except Exception as e:
            self._start_error = f"libp2p_unavailable:{e}"
            self._libp2p_available = False
            self._started = False
            return False, self._start_error

        self._libp2p_available = True

        self._trio_stop = threading.Event()

        def _run_trio() -> None:
            async def _main() -> None:
                try:
                    self._trio_token = trio.lowlevel.current_trio_token()

                    host = new_host()
                    router = GossipSub(
                        [PROTOCOL_ID, PROTOCOL_ID_V11, PROTOCOL_ID_V12],
                        degree=6,
                        degree_low=4,
                        degree_high=12,
                    )
                    pubsub = Pubsub(host, router)

                    self._host = host
                    self._pubsub = pubsub

                    net = host.get_network()
                    for addr in self.config.listen_multiaddrs:
                        try:
                            await net.listen(Multiaddr(addr))
                        except Exception:
                            pass

                    self.peer_id = self._safe_get_peer_id(host)
                    self.listen_addrs = [str(a) for a in getattr(net, "listeners", [])]

                    print("[LATTICE_P2P] started")
                    print(f"[LATTICE_P2P] peer_id={self.peer_id}")
                    if self.listen_addrs:
                        for a in self.listen_addrs:
                            print(f"[LATTICE_P2P] listen={a}")

                    for peer in self.config.bootstrap_peers:
                        try:
                            pinfo = info_from_p2p_addr(Multiaddr(peer))
                            host.get_peerstore().add_addrs(pinfo.peer_id, pinfo.addrs, PERMANENT_ADDR_TTL)
                            await host.connect(pinfo)
                        except Exception:
                            pass

                    sub = await pubsub.subscribe(self.config.topic)

                    async def _recv_loop() -> None:
                        while not self._trio_stop.is_set():
                            try:
                                msg = await sub.get()
                                self._rx_queue.put({"data": getattr(msg, "data", None)})
                            except Exception:
                                await trio.sleep(0.05)

                    async with trio.open_nursery() as nursery:
                        nursery.start_soon(host.run)
                        nursery.start_soon(pubsub.run)
                        nursery.start_soon(_recv_loop)
                        while not self._trio_stop.is_set():
                            await trio.sleep(0.1)
                        nursery.cancel_scope.cancel()
                except Exception as e:
                    self._start_error = f"p2p_start_failed:{e}"

            try:
                trio.run(_main)
            except Exception as e:
                self._start_error = f"p2p_start_failed:{e}"

        self._trio_thread = threading.Thread(target=_run_trio, name="aethel-libp2p", daemon=True)
        self._trio_thread.start()

        self._start_error = None

        async def _pump_rx() -> None:
            while self._started:
                try:
                    item = await asyncio.to_thread(self._rx_queue.get)
                    await self._on_message(item)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.05)

        self._started = True
        self._sub_task = asyncio.create_task(_pump_rx())

        # Aguardar até 10 segundos (200 iterações x 50ms) para peer_id estar pronto
        max_attempts = 200
        for attempt in range(max_attempts):
            if self._start_error is not None:
                print(f"[LATTICE_P2P] start_error detected: {self._start_error}")
                break
            if self._trio_token is not None and self.peer_id:
                print(f"[LATTICE_P2P] peer_id ready after {attempt} attempts ({attempt * 50}ms)")
                break
            if attempt % 20 == 0 and attempt > 0:
                print(f"[LATTICE_P2P] waiting for peer_id... attempt {attempt}/{max_attempts}")
            await asyncio.sleep(0.05)

        if self._start_error is not None:
            return False, self._start_error

        if self._trio_token is None or not self.peer_id:
            self._start_error = f"p2p_start_timeout (trio_token={self._trio_token is not None}, peer_id={self.peer_id})"
            self._started = False
            print(f"[LATTICE_P2P] timeout: {self._start_error}")
            return False, self._start_error

        print(f"[LATTICE_P2P] successfully started with peer_id={self.peer_id}")
        return True, "p2p_started"

    async def stop(self) -> None:
        self._started = False
        try:
            if self._trio_stop is not None:
                self._trio_stop.set()
        except Exception:
            pass
        try:
            if self._sub_task is not None:
                self._sub_task.cancel()
        except Exception:
            pass
        self._host = None
        self._pubsub = None
        self._sub_task = None
        self._trio_thread = None
        self._trio_stop = None
        self._trio_token = None
        self.peer_id = None
        self.listen_addrs = []

    def _safe_get_peer_id(self, host: Any) -> Optional[str]:
        try:
            pid = getattr(host, "get_id")()
            if hasattr(pid, "pretty"):
                result = pid.pretty()
                print(f"[LATTICE_P2P] extracted peer_id via pretty(): {result}")
                return result
            result = str(pid)
            print(f"[LATTICE_P2P] extracted peer_id via str(): {result}")
            return result
        except Exception as e:
            print(f"[LATTICE_P2P] failed to extract peer_id: {e}")
            return None

    def _safe_get_listen_addrs(self, host: Any) -> List[str]:
        addrs: List[str] = []
        try:
            network = getattr(host, "network", None)
            if network is None:
                return []
            listen_addrs = getattr(network, "get_listen_addrs", None)
            if callable(listen_addrs):
                for a in listen_addrs():
                    addrs.append(str(a))
        except Exception:
            return []
        return addrs

    async def publish_proof_event(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        if not self.config.enabled:
            return False, "p2p_disabled"

        if not self._started or not self._pubsub:
            return False, "p2p_not_started"

        try:
            msg = {
                "type": "proof_event",
                "timestamp": time.time(),
                "merkle_root": self.persistence.merkle_db.get_root(),
                "payload": payload,
                # CRITICAL FIX (RVC3-003): Include peer_id in messages for heartbeat tracking
                "peer_id": self.peer_id,
            }
            data = json.dumps(msg, sort_keys=True).encode("utf-8")
            if self._trio_token is None:
                for _ in range(40):
                    if self._trio_token is not None:
                        break
                    await asyncio.sleep(0.05)
            if self._trio_token is None:
                return False, "p2p_not_ready"
            import trio  # type: ignore
            await asyncio.to_thread(
                trio.from_thread.run,
                self._pubsub.publish,
                self.config.topic,
                data,
                trio_token=self._trio_token,
            )
            print(f"[LATTICE_P2P] published proof_event topic={self.config.topic} intent={payload.get('intent')}")
            return True, "published"
        except Exception as e:
            return False, f"publish_failed:{e}"

    async def _on_message(self, msg) -> None:
        try:
            data = None
            if isinstance(msg, dict):
                data = msg.get("data")
            else:
                data = getattr(msg, "data", None)
            if not data:
                return
            if isinstance(data, (bytes, bytearray)):
                raw = data.decode("utf-8")
            else:
                raw = str(data)
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                return
            if parsed.get("type") != "proof_event":
                return

            # CRITICAL FIX (RVC3-003): Update heartbeat timestamp for peer
            peer_id = parsed.get("peer_id")
            if peer_id:
                self._peer_heartbeats[peer_id] = time.time()
                print(f"[LATTICE_P2P] heartbeat updated for peer {peer_id}")

            try:
                intent = parsed.get("payload", {}).get("intent")
            except Exception:
                intent = None
            print(f"[LATTICE_P2P] received proof_event topic={self.config.topic} intent={intent}")

            peer_root = parsed.get("merkle_root")
            if isinstance(peer_root, str) and peer_root and (not self.persistence.merkle_db.state):
                http_peers = os.getenv("AETHEL_LATTICE_NODES", "").strip()
                if http_peers:
                    peer_urls = [s.strip() for s in http_peers.split(",") if s.strip()]
                    sync_state_if_empty(self.persistence, peer_urls)
        except Exception:
            return


_global_streams: Optional[LatticeStreams] = None


def get_lattice_streams(persistence: AethelPersistenceLayer) -> LatticeStreams:
    global _global_streams
    if _global_streams is None:
        _global_streams = LatticeStreams(LatticeP2PConfig.from_env(), persistence)
    return _global_streams
