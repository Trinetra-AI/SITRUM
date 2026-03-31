# app/upgrades/pro_structure_engine.py

import pandas as pd

from app.config import (
    SWING_LOOKBACK,
    BOS_LOOKBACK,
    LIQUIDITY_SWEEP_WICK_RATIO,
)
from app.upgrades.pro_config import (
    MIN_BREAKOUT_CLOSE_ATR,
    MIN_RETEST_HOLD_ATR,
    MIN_SWEEP_REJECTION_BODY_RATIO,
    MIN_SWEEP_WICK_TO_BODY,
)
from app.utils.math_utils import wick_ratio
from app.utils.candle_utils import get_candle_stats


class ProStructureEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def detect_swings(self) -> pd.DataFrame:
        df = self.df.copy()
        df["swing_high"] = False
        df["swing_low"] = False

        for i in range(SWING_LOOKBACK, len(df) - SWING_LOOKBACK):
            current_high = df.iloc[i]["high"]
            current_low = df.iloc[i]["low"]

            left_highs = df.iloc[i - SWING_LOOKBACK:i]["high"]
            right_highs = df.iloc[i + 1:i + 1 + SWING_LOOKBACK]["high"]

            left_lows = df.iloc[i - SWING_LOOKBACK:i]["low"]
            right_lows = df.iloc[i + 1:i + 1 + SWING_LOOKBACK]["low"]

            if current_high > left_highs.max() and current_high > right_highs.max():
                df.at[df.index[i], "swing_high"] = True

            if current_low < left_lows.min() and current_low < right_lows.min():
                df.at[df.index[i], "swing_low"] = True

        return df

    def detect_structure_bias(self, df: pd.DataFrame) -> str:
        highs = df[df["swing_high"]]["high"].tail(3).tolist()
        lows = df[df["swing_low"]]["low"].tail(3).tolist()

        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                return "bullish"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                return "bearish"

        return "neutral"

    def detect_break_of_structure(self, df: pd.DataFrame) -> dict:
        recent = df.tail(BOS_LOOKBACK)
        latest = recent.iloc[-1]

        swing_highs = recent[recent["swing_high"]]
        swing_lows = recent[recent["swing_low"]]

        last_swing_high = swing_highs["high"].iloc[-1] if len(swing_highs) > 0 else None
        last_swing_low = swing_lows["low"].iloc[-1] if len(swing_lows) > 0 else None

        bos_up = last_swing_high is not None and latest["close"] > last_swing_high
        bos_down = last_swing_low is not None and latest["close"] < last_swing_low

        return {
            "bos_up": bos_up,
            "bos_down": bos_down,
            "last_swing_high": float(last_swing_high) if last_swing_high is not None else None,
            "last_swing_low": float(last_swing_low) if last_swing_low is not None else None,
        }

    def detect_liquidity_sweep(self, df: pd.DataFrame) -> dict:
        if len(df) < 5:
            return {"sweep_high": False, "sweep_low": False}

        latest = df.iloc[-1]
        previous = df.iloc[-5:-1]
        stats = get_candle_stats(latest)

        highest_prev = previous["high"].max()
        lowest_prev = previous["low"].min()

        wr = wick_ratio(latest["open"], latest["high"], latest["low"], latest["close"])

        sweep_high = (
            latest["high"] > highest_prev and
            latest["close"] < highest_prev and
            wr["upper_wick_to_body"] > max(LIQUIDITY_SWEEP_WICK_RATIO, MIN_SWEEP_WICK_TO_BODY) and
            stats["body_ratio"] >= MIN_SWEEP_REJECTION_BODY_RATIO
        )

        sweep_low = (
            latest["low"] < lowest_prev and
            latest["close"] > lowest_prev and
            wr["lower_wick_to_body"] > max(LIQUIDITY_SWEEP_WICK_RATIO, MIN_SWEEP_WICK_TO_BODY) and
            stats["body_ratio"] >= MIN_SWEEP_REJECTION_BODY_RATIO
        )

        return {
            "sweep_high": sweep_high,
            "sweep_low": sweep_low,
            "reference_high": float(highest_prev),
            "reference_low": float(lowest_prev),
        }

    def detect_breakout_retest(self, df: pd.DataFrame) -> dict:
        if len(df) < 12:
            return {
                "bullish_breakout_retest": False,
                "bearish_breakout_retest": False,
                "weak_breakout": True,
            }

        recent = df.tail(12).copy()
        latest = recent.iloc[-1]
        atr = latest["atr"] if "atr" in latest and latest["atr"] == latest["atr"] else 1.0

        prior_high = recent["high"].iloc[:-2].max()
        prior_low = recent["low"].iloc[:-2].min()

        breakout_close_up = latest["close"] - prior_high
        breakout_close_down = prior_low - latest["close"]

        bullish_breakout = (
            latest["close"] > prior_high and
            breakout_close_up >= atr * MIN_BREAKOUT_CLOSE_ATR and
            latest["low"] <= prior_high + (atr * MIN_RETEST_HOLD_ATR)
        )

        bearish_breakout = (
            latest["close"] < prior_low and
            breakout_close_down >= atr * MIN_BREAKOUT_CLOSE_ATR and
            latest["high"] >= prior_low - (atr * MIN_RETEST_HOLD_ATR)
        )

        weak_breakout = not bullish_breakout and not bearish_breakout and (
            latest["high"] > prior_high or latest["low"] < prior_low
        )

        return {
            "bullish_breakout_retest": bullish_breakout,
            "bearish_breakout_retest": bearish_breakout,
            "weak_breakout": weak_breakout,
            "breakout_high_level": float(prior_high),
            "breakout_low_level": float(prior_low),
        }

    def analyze(self) -> dict:
        df = self.detect_swings()

        structure_bias = self.detect_structure_bias(df)
        bos = self.detect_break_of_structure(df)
        sweep = self.detect_liquidity_sweep(df)
        breakout = self.detect_breakout_retest(df)

        score = 35
        if structure_bias in ["bullish", "bearish"]:
            score += 20
        if bos["bos_up"] or bos["bos_down"]:
            score += 15
        if breakout["bullish_breakout_retest"] or breakout["bearish_breakout_retest"]:
            score += 20
        if sweep["sweep_high"] or sweep["sweep_low"]:
            score += 10
        if breakout.get("weak_breakout", False):
            score -= 10

        return {
            "structure_bias": structure_bias,
            "score": max(0, min(score, 100)),
            "bos": bos,
            "liquidity_sweep": sweep,
            "breakout_retest": breakout,
        }