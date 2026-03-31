# app/core/macro_filter_engine.py

import pandas as pd
from pathlib import Path

from app.config import (
    MACRO_EVENTS_FILE,
    MACRO_BLOCK_MINUTES_BEFORE,
    MACRO_BLOCK_MINUTES_AFTER,
    HIGH_IMPACT_EVENTS,
)
from app.utils.time_utils import ensure_datetime_utc, minutes_between


class MacroFilterEngine:
    def __init__(self, current_time: pd.Timestamp):
        self.current_time = current_time

    def load_events(self) -> pd.DataFrame:
        filepath = Path(MACRO_EVENTS_FILE)

        if not filepath.exists():
            return pd.DataFrame(columns=["time", "event", "impact", "currency"])

        df = pd.read_csv(filepath)
        if "time" not in df.columns or "event" not in df.columns:
            return pd.DataFrame(columns=["time", "event", "impact", "currency"])

        df = ensure_datetime_utc(df, "time")
        return df.dropna(subset=["time"]).copy()

    def analyze(self) -> dict:
        df = self.load_events()

        if df.empty:
            return {
                "blocked": False,
                "score": 80,
                "reason": "No macro events file or no events found.",
                "nearest_event": None,
                "minutes_to_event": None,
            }

        nearest_event = None
        nearest_minutes = None
        blocked = False
        reason = "No dangerous macro event nearby."
        score = 80

        for _, row in df.iterrows():
            event_time = row["time"]
            event_name = str(row.get("event", "")).upper()
            impact = str(row.get("impact", "")).lower()
            currency = str(row.get("currency", "")).upper()

            mins = minutes_between(self.current_time, event_time)

            if nearest_minutes is None or mins < nearest_minutes:
                nearest_minutes = mins
                nearest_event = {
                    "time": str(event_time),
                    "event": row.get("event", ""),
                    "impact": impact,
                    "currency": currency,
                }

            is_high_impact = impact == "high" or event_name in HIGH_IMPACT_EVENTS

            if is_high_impact and currency in ["USD", "XAU", "ALL", ""]:
                if event_time >= self.current_time:
                    if mins <= MACRO_BLOCK_MINUTES_BEFORE:
                        blocked = True
                        reason = f"High-impact macro event approaching: {row.get('event', '')}"
                        score = 10
                else:
                    if mins <= MACRO_BLOCK_MINUTES_AFTER:
                        blocked = True
                        reason = f"High-impact macro event just passed: {row.get('event', '')}"
                        score = 20

        return {
            "blocked": blocked,
            "score": score,
            "reason": reason,
            "nearest_event": nearest_event,
            "minutes_to_event": round(nearest_minutes, 2) if nearest_minutes is not None else None,
        }