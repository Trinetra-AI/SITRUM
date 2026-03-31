# app/core/zone_engine.py

import pandas as pd
from app.config import ZONE_LOOKBACK, SR_CLUSTER_TOLERANCE


class ZoneEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_recent_levels(self) -> dict:
        recent = self.df.tail(ZONE_LOOKBACK)

        return {
            "recent_high": float(recent["high"].max()),
            "recent_low": float(recent["low"].min()),
            "recent_mid": float((recent["high"].max() + recent["low"].min()) / 2),
        }

    def get_previous_day_levels(self) -> dict:
        df = self.df.copy()
        df["date"] = df["time"].dt.date

        unique_days = df["date"].unique()
        if len(unique_days) < 2:
            return {
                "prev_day_high": None,
                "prev_day_low": None,
                "prev_day_close": None,
            }

        prev_day = unique_days[-2]
        prev_df = df[df["date"] == prev_day]

        return {
            "prev_day_high": float(prev_df["high"].max()),
            "prev_day_low": float(prev_df["low"].min()),
            "prev_day_close": float(prev_df["close"].iloc[-1]),
        }

    def get_support_resistance(self) -> dict:
        recent = self.df.tail(ZONE_LOOKBACK)
        highs = recent["high"].round(1).value_counts()
        lows = recent["low"].round(1).value_counts()

        resistance_candidates = highs[highs >= 2].index.tolist()
        support_candidates = lows[lows >= 2].index.tolist()

        resistance = float(max(resistance_candidates)) if resistance_candidates else float(recent["high"].max())
        support = float(min(support_candidates)) if support_candidates else float(recent["low"].min())

        return {
            "support": support,
            "resistance": resistance,
        }

    def classify_price_location(self, close: float, support: float, resistance: float) -> str:
        if abs(close - support) <= SR_CLUSTER_TOLERANCE:
            return "near_support"
        elif abs(close - resistance) <= SR_CLUSTER_TOLERANCE:
            return "near_resistance"
        elif support < close < resistance:
            return "inside_range"
        return "outside_range"

    def analyze(self) -> dict:
        latest = self.df.iloc[-1]
        levels = self.get_recent_levels()
        pd_levels = self.get_previous_day_levels()
        sr = self.get_support_resistance()

        location = self.classify_price_location(
            close=latest["close"],
            support=sr["support"],
            resistance=sr["resistance"],
        )

        score = 50
        if location in ["near_support", "near_resistance"]:
            score += 20

        return {
            "score": score,
            "price_location": location,
            "recent_levels": levels,
            "previous_day_levels": pd_levels,
            "support_resistance": sr,
        }