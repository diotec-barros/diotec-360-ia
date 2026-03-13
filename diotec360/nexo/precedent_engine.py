"""Aethel Proof-of-Precedent Engine (PoP v0.1)

A tiny precedent index + query layer backed by a JSON file inside the Vault.

Design goals:
- Deterministic (no embeddings yet).
- Works offline (local vault), but can later be mirrored to GunDB.
- Query by intent/tags/tokens with simple ranking.

Storage format: `.aethel_vault/precedents.json`
{
  "v": 1,
  "items": {
     "<record_hash>": { ... precedent record ... }
  }
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _lower_set(xs: Iterable[str]) -> set[str]:
    return {str(x).strip().lower() for x in xs if str(x).strip()}


def _score(
    *,
    query_intent: Optional[str],
    query_tags: set[str],
    query_tokens: set[str],
    item: Dict[str, Any],
) -> float:
    s = 0.0

    if query_intent:
        if str(item.get("intent_name", "")).strip().lower() == query_intent:
            s += 5.0
        elif query_intent in str(item.get("intent_name", "")).strip().lower():
            s += 2.0

    item_tags = _lower_set(item.get("tags") or [])
    item_tokens = _lower_set(item.get("tokens") or [])

    tag_overlap = len(query_tags.intersection(item_tags))
    tok_overlap = len(query_tokens.intersection(item_tokens))

    s += tag_overlap * 1.5
    s += tok_overlap * 0.3

    if str(item.get("status", "")).upper() == "PROVED":
        s += 1.0

    return s


@dataclass
class PrecedentQuery:
    intent_name: Optional[str] = None
    tags: Optional[List[str]] = None
    tokens: Optional[List[str]] = None
    limit: int = 10


class PrecedentEngine:
    def __init__(self, vault_path: str = ".aethel_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.path = self.vault_path / "precedents.json"
        self._cache: Optional[Dict[str, Any]] = None

    def _load(self) -> Dict[str, Any]:
        if self._cache is not None:
            return self._cache
        if not self.path.exists():
            self._cache = {"v": 1, "items": {}}
            return self._cache
        with open(self.path, "r", encoding="utf-8") as f:
            self._cache = json.load(f)
        if not isinstance(self._cache, dict) or "items" not in self._cache:
            self._cache = {"v": 1, "items": {}}
        if not isinstance(self._cache.get("items"), dict):
            self._cache["items"] = {}
        return self._cache

    def _save(self, data: Dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.path)
        self._cache = data

    def upsert(self, record: Dict[str, Any]) -> str:
        data = self._load()
        items: Dict[str, Any] = data["items"]
        rid = str(record.get("record_hash") or "").strip()
        if not rid:
            raise ValueError("PrecedentEngine.upsert: record_hash missing")
        items[rid] = record
        self._save(data)
        return rid

    def get(self, record_hash: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data.get("items", {}).get(record_hash)

    def query(self, q: PrecedentQuery) -> List[Dict[str, Any]]:
        data = self._load()
        items = list((data.get("items") or {}).values())

        query_intent = q.intent_name.strip().lower() if q.intent_name else None
        query_tags = _lower_set(q.tags or [])
        query_tokens = _lower_set(q.tokens or [])

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for it in items:
            sc = _score(query_intent=query_intent, query_tags=query_tags, query_tokens=query_tokens, item=it)
            if sc <= 0:
                continue
            scored.append((sc, it))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [it for _, it in scored[: max(1, int(q.limit or 10))]]

    def list_all(self) -> List[Dict[str, Any]]:
        data = self._load()
        return list((data.get("items") or {}).values())
