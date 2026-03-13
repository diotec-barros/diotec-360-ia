import os
from dataclasses import dataclass
from typing import List, Optional

from diotec360.core.env_compat import getbool, getenv


@dataclass
class EnvGuardReport:
    production: bool
    safe_mode: bool
    violations: List[str]

    def ok(self) -> bool:
        return len(self.violations) == 0


def _is_truthy(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_production() -> bool:
    return (getenv("DIOTEC360_ENV", legacy="AETHEL_ENV", default="") or "").strip().lower() == "production"


def validate_environment() -> EnvGuardReport:
    production = is_production()
    safe_mode = getbool("DIOTEC360_SAFE_MODE", legacy="AETHEL_SAFE_MODE", default=False)
    violations: List[str] = []
    critical: List[str] = []

    if not production:
        return EnvGuardReport(production=False, safe_mode=safe_mode, violations=[])

    cors_raw = (getenv("DIOTEC360_CORS_ORIGINS", legacy="AETHEL_CORS_ORIGINS", default="") or "").strip()
    if not cors_raw:
        msg = "AETHEL_CORS_ORIGINS is required in production"
        violations.append(msg)
        critical.append(msg)
    else:
        origins = [o.strip() for o in cors_raw.split(",") if o.strip()]
        if not origins:
            msg = "AETHEL_CORS_ORIGINS is empty in production"
            violations.append(msg)
            critical.append(msg)
        if any(o == "*" for o in origins):
            msg = "AETHEL_CORS_ORIGINS must not contain '*' in production"
            violations.append(msg)
            critical.append(msg)

    if os.getenv("ALPHA_VANTAGE_API_KEY", "demo").strip().lower() == "demo":
        msg = "ALPHA_VANTAGE_API_KEY is 'demo' in production"
        violations.append(msg)
        critical.append(msg)

    if getbool("DIOTEC360_TEST_MODE", legacy="AETHEL_TEST_MODE", default=False):
        msg = "AETHEL_TEST_MODE must be disabled in production"
        violations.append(msg)
        critical.append(msg)

    if getbool("DIOTEC360_OFFLINE", legacy="AETHEL_OFFLINE", default=False):
        msg = "AETHEL_OFFLINE must be disabled in production"
        violations.append(msg)
        critical.append(msg)

    if _is_truthy(os.getenv("PAYPAL_SANDBOX")):
        msg = "PAYPAL_SANDBOX must be 0 in production"
        violations.append(msg)
        critical.append(msg)

    if _is_truthy(os.getenv("MULTICAIXA_SANDBOX")):
        msg = "MULTICAIXA_SANDBOX must be 0 in production"
        violations.append(msg)
        critical.append(msg)

    p2p_enabled = getbool("DIOTEC360_P2P_ENABLED", legacy="AETHEL_P2P_ENABLED", default=False)
    if p2p_enabled:
        bootstrap = (getenv("DIOTEC360_P2P_BOOTSTRAP", legacy="AETHEL_P2P_BOOTSTRAP", default="") or "").strip()
        if not bootstrap:
            msg = "AETHEL_P2P_BOOTSTRAP is required when AETHEL_P2P_ENABLED=1 in production"
            violations.append(msg)
            critical.append(msg)

    next_public_gun_peers = os.getenv("NEXT_PUBLIC_GUN_PEERS", "").strip()
    if not next_public_gun_peers:
        violations.append("NEXT_PUBLIC_GUN_PEERS should be configured in production (prevents in-memory-only registry)")

    if critical and not safe_mode:
        os.environ["DIOTEC360_SAFE_MODE"] = "1"
        os.environ["AETHEL_SAFE_MODE"] = "1"
        safe_mode = True

    return EnvGuardReport(production=True, safe_mode=safe_mode, violations=violations)


def print_report(report: EnvGuardReport) -> None:
    if not report.production:
        return

    if report.ok():
        print("[ENV_GUARD] OK - production environment validated")
        return

    print("[ENV_GUARD] VIOLATIONS DETECTED")
    for v in report.violations:
        print(f"[ENV_GUARD] - {v}")

    if report.safe_mode:
        print("[ENV_GUARD] SAFE MODE ENABLED (AETHEL_SAFE_MODE=1)")
