# app/upgrades/market_regime_engine.py

import pandas as pd
from app.upgrades.pro_config import RANGE_ATR_THRESHOLD, TREND_ATR_THRESHOLD


class MarketRegimeEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        if len(self.df) < 30:
            return {
                "regime": "unknown",
                "score": 40,
                "range_size": None,
                "atr": None,
            }

        recent = self.df.tail(30)
        highest = recent["high"].max()
        lowest = recent["low"].min()
        range_size = highest - lowest
        atr = recent["atr"].iloc[-1] if "atr" in recent.columns else None

        if atr is None or atr != atr or atr == 0:
            return {
                "regime": "unknown",
                "score": 40,
                "range_size": float(range_size),
                "atr": None,
            }

        ratio = range_size / atr

        if ratio >= TREND_ATR_THRESHOLD:
            regime = "trending"
            score = 85
        elif ratio <= RANGE_ATR_THRESHOLD:
            regime = "tight_range"
            score = 35
        else:
            regime = "mixed"
            score = 55

        return {
            "regime": regime,
            "score": score,
            "range_size": float(range_size),
            "atr": float(atr),
            "range_atr_ratio": round(ratio, 2),
        }