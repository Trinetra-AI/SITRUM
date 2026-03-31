# app/utils/time_utils.py

import pandas as pd
from datetime import datetime, timezone


def ensure_datetime_utc(df: pd.DataFrame, column: str = "time") -> pd.DataFrame:
    df = df.copy()
    df[column] = pd.to_datetime(df[column], utc=True, errors="coerce")
    return df


def get_utc_hour(ts: pd.Timestamp) -> int:
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.hour


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def minutes_between(a: pd.Timestamp, b: pd.Timestamp) -> float:
    return abs((a - b).total_seconds()) / 60.0


def is_within_session(hour: int, session_range: tuple) -> bool:
    start, end = session_range
    return start <= hour < end


def classify_session(hour: int, asian: tuple, london: tuple, new_york: tuple) -> str:
    sessions = []

    if is_within_session(hour, asian):
        sessions.append("asian")
    if is_within_session(hour, london):
        sessions.append("london")
    if is_within_session(hour, new_york):
        sessions.append("new_york")

    if not sessions:
        return "off_session"

    if len(sessions) == 2:
        return "_".join(sessions) + "_overlap"

    return sessions[0]