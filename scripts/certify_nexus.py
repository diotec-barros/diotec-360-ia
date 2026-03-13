#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx


@dataclass
class CheckResult:
    name: str
    ok: bool
    duration_ms: float
    details: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ms(start: float, end: float) -> float:
    return (end - start) * 1000.0


def _write_certificate(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fail_exit_code(results: List[CheckResult]) -> int:
    # 0 = bank-ready
    # 2 = certification failed
    return 0 if all(r.ok for r in results) else 2


def check_integrity(base_url: str, timeout_s: float) -> CheckResult:
    t0 = time.perf_counter()
    details: Dict[str, Any] = {}
    ok = False

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(f"{base_url}/api/status")
            details["http_status"] = r.status_code
            data = r.json()
            details["response"] = data

        production = bool(data.get("production"))
        safe_mode = bool(data.get("safe_mode"))

        ok = production and (not safe_mode)
        details["production"] = production
        details["safe_mode"] = safe_mode

        if not production:
            details["error"] = "DIOTEC360_ENV is not production (production=false)"
        elif safe_mode:
            details["error"] = "Safe Mode is enabled (safe_mode=true)"

    except Exception as e:
        details["error"] = str(e)

    t1 = time.perf_counter()
    return CheckResult(name="integrity", ok=ok, duration_ms=_ms(t0, t1), details=details)


def check_forex_heartbeat(timeout_s: float) -> CheckResult:
    t0 = time.perf_counter()
    details: Dict[str, Any] = {}
    ok = False

    try:
        # Local import to avoid import-cost in environments that only want partial checks.
        from diotec360.core.real_forex_api import get_real_forex_oracle

        oracle = get_real_forex_oracle()

        # In certification, we require real quotes (no test_mode/offline)
        details["oracle_test_mode"] = bool(getattr(oracle, "test_mode", False))

        if details["oracle_test_mode"]:
            details["error"] = "Oracle is in test_mode/offline; disable DIOTEC360_TEST_MODE/DIOTEC360_OFFLINE"
        else:
            import asyncio

            async def _run():
                return await oracle.get_quote("EUR/USD")

            quote = asyncio.run(_run())

            if not quote:
                details["error"] = "No quote returned (possibly rate-limit or invalid API key)"
            else:
                details["pair"] = quote.pair
                details["provider"] = quote.provider
                details["price"] = quote.price
                details["timestamp"] = quote.timestamp
                details["seal"] = quote.authenticity_seal

                valid = oracle.validate_quote(quote)
                details["seal_valid"] = bool(valid)

                # If provider is alpha_vantage and API is rate-limited, quote would be None in current implementation.
                ok = bool(valid) and quote.provider != "test_mode"

    except Exception as e:
        details["error"] = str(e)

    t1 = time.perf_counter()
    return CheckResult(name="forex_heartbeat", ok=ok, duration_ms=_ms(t0, t1), details=details)


def check_lattice_ping(base_url: str, timeout_s: float, min_peers: int) -> CheckResult:
    t0 = time.perf_counter()
    details: Dict[str, Any] = {}
    ok = False

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(f"{base_url}/api/lattice/p2p/status")
            details["http_status"] = r.status_code
            data = r.json()
            details["response"] = data

        enabled = bool(data.get("enabled"))
        started = bool(data.get("started"))
        peer_count = int(data.get("peer_count") or 0)

        details["enabled"] = enabled
        details["started"] = started
        details["peer_count"] = peer_count
        details["min_peers"] = min_peers

        ok = enabled and started and peer_count >= min_peers

        if not enabled:
            details["error"] = "P2P disabled (DIOTEC360_P2P_ENABLED != 1)"
        elif not started:
            details["error"] = "P2P not started (libp2p unavailable or startup failed)"
        elif peer_count < min_peers:
            details["error"] = f"Not enough peers (peer_count={peer_count} < {min_peers})"

    except Exception as e:
        details["error"] = str(e)

    t1 = time.perf_counter()
    return CheckResult(name="lattice_ping", ok=ok, duration_ms=_ms(t0, t1), details=details)


def check_math_stress(base_url: str, timeout_s: float, max_ms: float) -> CheckResult:
    t0 = time.perf_counter()
    details: Dict[str, Any] = {}
    ok = False

    # Constraint set that forces arithmetic parsing and should be SAT.
    # We don't depend on an internal "prove" endpoint; we use /api/verify which already runs Z3.
    # Note: code format must be compatible with the parser used by backend.
    code = """intent certify_math(a: Int, b: Int, c: Int) {
    guard {
        c > 0;
    }

    verify {
        (a + b) * c == (a * c) + (b * c);
    }
}"""

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(f"{base_url}/api/verify", json={"code": code})
            details["http_status"] = r.status_code
            data = r.json()
            details["response"] = data

        verdict = str(data.get("status") or "")
        success = bool(data.get("success"))

        details["verdict"] = verdict
        details["success"] = success

        t1 = time.perf_counter()
        duration_ms = _ms(t0, t1)
        details["max_ms"] = max_ms

        ok = success and verdict == "PROVED" and duration_ms <= max_ms

        if not success or verdict != "PROVED":
            details["error"] = "Backend judge did not return PROVED"
        elif duration_ms > max_ms:
            details["error"] = f"Judge took too long ({duration_ms:.1f}ms > {max_ms}ms)"

        return CheckResult(name="math_stress", ok=ok, duration_ms=duration_ms, details=details)

    except Exception as e:
        details["error"] = str(e)

    t1 = time.perf_counter()
    return CheckResult(name="math_stress", ok=ok, duration_ms=_ms(t0, t1), details=details)


def main() -> int:
    ap = argparse.ArgumentParser(description="DIOTEC360-Certify (Nexus Certification Script)")
    ap.add_argument(
        "--base-url",
        default=os.getenv("DIOTEC360_API_URL") or os.getenv("DIOTEC360_API_URL") or "http://127.0.0.1:8000",
        help="DIOTEC 360 IA API base URL",
    )
    ap.add_argument("--timeout", type=float, default=6.0, help="HTTP timeout seconds")
    ap.add_argument("--min-peers", type=int, default=1, help="Minimum required P2P peers")
    ap.add_argument("--math-max-ms", type=float, default=500.0, help="Max allowed ms for math verify")
    ap.add_argument("--out", default="CERTIFICATE_V3_1_1.json", help="Output certificate JSON filename")
    args = ap.parse_args()

    base_url = args.base_url.rstrip("/")
    started_at = _utc_now_iso()

    results: List[CheckResult] = []

    results.append(check_integrity(base_url, timeout_s=args.timeout))
    results.append(check_forex_heartbeat(timeout_s=args.timeout))
    results.append(check_lattice_ping(base_url, timeout_s=args.timeout, min_peers=args.min_peers))
    results.append(check_math_stress(base_url, timeout_s=args.timeout, max_ms=args.math_max_ms))

    finished_at = _utc_now_iso()

    certificate: Dict[str, Any] = {
        "certificate": {
            "name": "DIOTEC360-CERTIFY",
            "version": "v3.1.1",
            "started_at": started_at,
            "finished_at": finished_at,
            "base_url": base_url,
        },
        "results": [
            {
                "name": r.name,
                "ok": r.ok,
                "duration_ms": r.duration_ms,
                "details": r.details,
            }
            for r in results
        ],
        "bank_ready": all(r.ok for r in results),
        "exit_code": _fail_exit_code(results),
    }

    out_path = Path(args.out)
    _write_certificate(out_path, certificate)

    # Human-readable summary to stdout (kept short)
    for r in results:
        status = "OK" if r.ok else "FAIL"
        print(f"[{status}] {r.name} ({r.duration_ms:.1f}ms)")
    print(f"Certificate: {out_path.resolve()}")
    print(f"Bank-ready: {certificate['bank_ready']}")

    return int(certificate["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
