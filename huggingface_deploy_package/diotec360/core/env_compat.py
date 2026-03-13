import os
from typing import Callable, Optional, TypeVar


T = TypeVar("T")


def getenv(primary: str, legacy: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(primary)
    if value is not None and value != "":
        return value
    if legacy:
        legacy_value = os.getenv(legacy)
        if legacy_value is not None and legacy_value != "":
            return legacy_value
    return default


def getbool(primary: str, legacy: Optional[str] = None, default: bool = False) -> bool:
    raw = getenv(primary, legacy=legacy, default=None)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def getcsv(primary: str, legacy: Optional[str] = None) -> list[str]:
    raw = getenv(primary, legacy=legacy, default="")
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


def with_prefix(primary_prefix: str, legacy_prefix: str) -> Callable[[str], tuple[str, str]]:
    def _mapper(suffix: str) -> tuple[str, str]:
        return f"{primary_prefix}{suffix}", f"{legacy_prefix}{suffix}"

    return _mapper
