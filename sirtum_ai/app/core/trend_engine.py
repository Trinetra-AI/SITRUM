# app/core/trend_engine.py

import pandas as pd
from app.config import EMA_FAST, EMA_MID, EMA_SLOW


class TrendEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        latest = self.df.iloc[-1]

        ema_fast = latest[f"ema_{EMA_FAST}"]
        ema_mid = latest[f"ema_{EMA_MID}"]
        ema_slow = latest[f"ema_{EMA_SLOW}"]
        close = latest["close"]

        bullish_alignment = ema_fast > ema_mid > ema_slow and close > ema_fast
        bearish_alignment = ema_fast < ema_mid < ema_slow and close < ema_fast

        if bullish_alignment:
            trend = "bullish"
            score = 85
        elif bearish_alignment:
            trend = "bearish"
            score = 85
        else:
            if close > ema_slow and ema_fast > ema_mid:
                trend = "bullish_weak"
                score = 60
            elif close < ema_slow and ema_fast < ema_mid:
                trend = "bearish_weak"
                score = 60
            else:
                trend = "sideways"
                score = 35

        return {
            "trend": trend,
            "score": score,
            "ema_fast": float(ema_fast),
            "ema_mid": float(ema_mid),
            "ema_slow": float(ema_slow),
            "close": float(close),
        }