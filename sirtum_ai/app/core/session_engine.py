# app/core/session_engine.py

import pandas as pd
from app.config import ASIAN_SESSION, LONDON_SESSION, NEW_YORK_SESSION
from app.utils.time_utils import get_utc_hour, classify_session


class SessionEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        latest = self.df.iloc[-1]
        latest_time = latest["time"]
        hour = get_utc_hour(latest_time)

        current_session = classify_session(
            hour=hour,
            asian=ASIAN_SESSION,
            london=LONDON_SESSION,
            new_york=NEW_YORK_SESSION,
        )

        session_quality = "neutral"
        score = 50

        if current_session in ["london", "new_york", "london_new_york_overlap"]:
            session_quality = "high_activity"
            score = 80
        elif current_session == "asian":
            session_quality = "moderate_activity"
            score = 55
        else:
            session_quality = "low_activity"
            score = 35

        return {
            "session": current_session,
            "session_quality": session_quality,
            "score": score,
            "utc_hour": hour,
            "timestamp": str(latest_time),
        }