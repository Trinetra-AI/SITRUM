# app/upgrades/pro_trend_engine.py

import pandas as pd
from app.config import EMA_FAST, EMA_MID, EMA_SLOW
from app.upgrades.pro_config import TREND_SLOPE_LOOKBACK, MIN_TREND_SLOPE_STRENGTH
from app.utils.math_utils import rolling_slope


class ProTrendEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        df = self.df.copy()

        df["ema_fast_slope"] = rolling_slope(df[f"ema_{EMA_FAST}"], TREND_SLOPE_LOOKBACK)
        df["ema_mid_slope"] = rolling_slope(df[f"ema_{EMA_MID}"], TREND_SLOPE_LOOKBACK)

        latest = df.iloc[-1]

        ema_fast = latest[f"ema_{EMA_FAST}"]
        ema_mid = latest[f"ema_{EMA_MID}"]
        ema_slow = latest[f"ema_{EMA_SLOW}"]
        close = latest["close"]

        fast_slope = latest["ema_fast_slope"]
        mid_slope = latest["ema_mid_slope"]

        bullish_alignment = ema_fast > ema_mid > ema_slow and close > ema_fast
        bearish_alignment = ema_fast < ema_mid < ema_slow and close < ema_fast

        strong_bull_slope = fast_slope > MIN_TREND_SLOPE_STRENGTH and mid_slope > 0
        strong_bear_slope = fast_slope < -MIN_TREND_SLOPE_STRENGTH and mid_slope < 0

        if bullish_alignment and strong_bull_slope:
            trend = "bullish_strong"
            score = 90
        elif bearish_alignment and strong_bear_slope:
            trend = "bearish_strong"
            score = 90
        elif bullish_alignment:
            trend = "bullish"
            score = 75
        elif bearish_alignment:
            trend = "bearish"
            score = 75
        else:
            if close > ema_slow:
                trend = "bullish_weak"
                score = 55
            elif close < ema_slow:
                trend = "bearish_weak"
                score = 55
            else:
                trend = "sideways"
                score = 30

        return {
            "trend": trend,
            "score": score,
            "ema_fast": float(ema_fast),
            "ema_mid": float(ema_mid),
            "ema_slow": float(ema_slow),
            "close": float(close),
            "ema_fast_slope": float(fast_slope) if fast_slope == fast_slope else None,
            "ema_mid_slope": float(mid_slope) if mid_slope == mid_slope else None,
        }