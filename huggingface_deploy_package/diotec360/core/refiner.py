"""Aethel Pattern Refiner (PoP v0.1)

Extracts a canonical "proof signature" from an intent AST (parser output).
The goal is to turn PROVED logic into reusable, queryable precedents.

This module is intentionally conservative:
- It does not attempt semantic embeddings.
- It normalizes constraints/verifications into stable strings.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def _cond_to_expr(cond: Any) -> str:
    if isinstance(cond, dict):
        return str(cond.get("expression", "")).strip()
    return str(cond).strip()


def _normalize_exprs(conds: Optional[List[Any]]) -> List[str]:
    out: List[str] = []
    for c in conds or []:
        s = _cond_to_expr(c)
        if s:
            out.append(s)
    return out


def _tokenize(s: str) -> List[str]:
    # Very small tokenizer for matching. Keep alnum + underscore.
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", s or "")
    return [t.lower() for t in toks]


def _stable_hash(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProofSignature:
    """Canonical extracted structure for a precedent."""

    intent_name: str
    constraints: List[str]
    post_conditions: List[str]
    ai_instructions: Dict[str, Any]
    signature_hash: str
    tokens: List[str]
    tags: List[str]


def extract_signature(intent_name: str, intent_ast: Dict[str, Any]) -> ProofSignature:
    """Extract a canonical signature from a single intent AST.

    `intent_ast` is expected to be produced by `AethelParser._transform_intent()`:
    {
      "params": [...],
      "constraints": [...],
      "ai_instructions": {...},
      "post_conditions": [...]
    }
    """

    constraints = sorted(_normalize_exprs(intent_ast.get("constraints")))
    post_conditions = sorted(_normalize_exprs(intent_ast.get("post_conditions")))
    ai_instructions = dict(intent_ast.get("ai_instructions") or {})

    signature_core = {
        "constraints": constraints,
        "post_conditions": post_conditions,
        "ai_instructions": ai_instructions,
    }
    signature_hash = _stable_hash(signature_core)

    tokens = sorted(set(_tokenize(" ".join(constraints + post_conditions))))

    tags: List[str] = []
    for k in ("priority", "target", "domain"):
        v = ai_instructions.get(k)
        if v:
            tags.append(f"{k}:{str(v).lower()}")

    # Also tag by intent name prefix/snake tokens.
    for t in _tokenize(intent_name):
        tags.append(f"intent:{t}")

    tags = sorted(set(tags))

    return ProofSignature(
        intent_name=intent_name,
        constraints=constraints,
        post_conditions=post_conditions,
        ai_instructions=ai_instructions,
        signature_hash=signature_hash,
        tokens=tokens,
        tags=tags,
    )


def build_precedent_record(
    *,
    intent_name: str,
    full_hash: str,
    logic_hash: str,
    intent_ast: Dict[str, Any],
    verification: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    sig = extract_signature(intent_name, intent_ast)
    record = {
        "v": 1,
        "intent_name": intent_name,
        "full_hash": full_hash,
        "logic_hash": logic_hash,
        "signature_hash": sig.signature_hash,
        "status": str((verification or {}).get("status", "")),
        "message": str((verification or {}).get("message", "")),
        "timestamp": str((verification or {}).get("timestamp", "")),
        "tags": sig.tags,
        "tokens": sig.tokens,
        "signature": {
            "constraints": sig.constraints,
            "post_conditions": sig.post_conditions,
            "ai_instructions": sig.ai_instructions,
        },
        "metadata": metadata or {},
    }
    record["record_hash"] = _stable_hash({k: record[k] for k in record.keys() if k != "record_hash"})
    return record
