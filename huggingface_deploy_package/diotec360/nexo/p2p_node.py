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

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from diotec360.core.persistence import AethelPersistenceLayer


def compute_merkle_root(state: Dict[str, Any]) -> str:
    if not state:
        return hashlib.sha256(b"empty").hexdigest()

    sorted_items = sorted(state.items())
    combined = ""
    for key, value in sorted_items:
        entry_hash = hashlib.sha256(f"{key}:{json.dumps(value)}".encode()).hexdigest()
        combined += entry_hash

    return hashlib.sha256(combined.encode()).hexdigest()


def _http_get_json(url: str, timeout_seconds: float = 5.0) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    req = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
            return True, json.loads(raw), "ok"
    except HTTPError as e:
        return False, None, f"http_error:{e.code}"
    except URLError as e:
        return False, None, f"url_error:{e.reason}"
    except Exception as e:
        return False, None, f"error:{e}"


def sync_state_if_empty(
    persistence: AethelPersistenceLayer,
    peer_http_urls: List[str],
    timeout_seconds: float = 5.0,
) -> Tuple[bool, str]:
    if persistence.merkle_db.state:
        return True, "local_state_present"

    for base_url in peer_http_urls:
        base = base_url.rstrip("/")
        ok, payload, reason = _http_get_json(f"{base}/api/lattice/state", timeout_seconds=timeout_seconds)
        if not ok or not payload:
            continue

        peer_state = payload.get("state")
        peer_root = payload.get("merkle_root")

        if not isinstance(peer_state, dict) or not isinstance(peer_root, str) or not peer_root:
            continue

        calculated = compute_merkle_root(peer_state)
        if calculated != peer_root:
            continue

        persistence.merkle_db.state = dict(peer_state)
        persistence.merkle_db.merkle_root = peer_root
        persistence.merkle_db.save_snapshot()
        return True, f"synced_from:{base}"

    return False, "no_peer_available"


@dataclass
class AethelLatticeNode:
    node_id: str
    http_listen_url: str
    bootstrap_http_peers: List[str]
    persistence: AethelPersistenceLayer

    def initial_sync(self) -> Tuple[bool, str]:
        return sync_state_if_empty(self.persistence, self.bootstrap_http_peers)
