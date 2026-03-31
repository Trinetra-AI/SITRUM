# app/utils/helpers.py

from typing import Any, Dict, Optional


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def round_if_number(value: Any, digits: int = 2) -> Any:
    if isinstance(value, (int, float)):
        return round(value, digits)
    return value


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def normalize_score(value: float, max_score: float = 100.0) -> float:
    if max_score == 0:
        return 0.0
    return clamp((value / max_score) * 100.0, 0.0, 100.0)


def dict_merge(a: Dict, b: Dict) -> Dict:
    result = a.copy()
    result.update(b)
    return result


def get_last_valid(series, default=None):
    if series is None or len(series) == 0:
        return default
    valid = series.dropna()
    if len(valid) == 0:
        return default
    return valid.iloc[-1]


def optional_get(d: Dict, key: str, default: Optional[Any] = None):
    return d[key] if key in d else default