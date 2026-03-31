# app/core/structure_engine.py

import pandas as pd
import numpy as np

from app.config import SWING_LOOKBACK, BOS_LOOKBACK, LIQUIDITY_SWEEP_WICK_RATIO
from app.utils.math_utils import wick_ratio


class StructureEngine:
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

    def get_recent_swings(self, df: pd.DataFrame) -> dict:
        swing_highs = df[df["swing_high"]].tail(5)
        swing_lows = df[df["swing_low"]].tail(5)

        return {
            "swing_highs": swing_highs[["time", "high"]].to_dict(orient="records"),
            "swing_lows": swing_lows[["time", "low"]].to_dict(orient="records"),
        }

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

        highest_prev = previous["high"].max()
        lowest_prev = previous["low"].min()

        wr = wick_ratio(latest["open"], latest["high"], latest["low"], latest["close"])

        sweep_high = latest["high"] > highest_prev and latest["close"] < highest_prev and wr["upper_wick_to_body"] > LIQUIDITY_SWEEP_WICK_RATIO
        sweep_low = latest["low"] < lowest_prev and latest["close"] > lowest_prev and wr["lower_wick_to_body"] > LIQUIDITY_SWEEP_WICK_RATIO

        return {
            "sweep_high": sweep_high,
            "sweep_low": sweep_low,
            "reference_high": float(highest_prev),
            "reference_low": float(lowest_prev),
        }

    def detect_breakout_retest(self, df: pd.DataFrame) -> dict:
        if len(df) < 10:
            return {
                "bullish_breakout_retest": False,
                "bearish_breakout_retest": False,
            }

        recent = df.tail(10).copy()
        highs = recent["high"].iloc[:-1]
        lows = recent["low"].iloc[:-1]
        latest = recent.iloc[-1]

        breakout_level_high = highs.max()
        breakout_level_low = lows.min()

        bullish_breakout = latest["close"] > breakout_level_high and latest["low"] <= breakout_level_high
        bearish_breakout = latest["close"] < breakout_level_low and latest["high"] >= breakout_level_low

        return {
            "bullish_breakout_retest": bullish_breakout,
            "bearish_breakout_retest": bearish_breakout,
            "breakout_high_level": float(breakout_level_high),
            "breakout_low_level": float(breakout_level_low),
        }

    def analyze(self) -> dict:
        df = self.detect_swings()

        structure_bias = self.detect_structure_bias(df)
        bos = self.detect_break_of_structure(df)
        sweep = self.detect_liquidity_sweep(df)
        breakout = self.detect_breakout_retest(df)
        swings = self.get_recent_swings(df)

        score = 40
        if structure_bias in ["bullish", "bearish"]:
            score += 20
        if bos["bos_up"] or bos["bos_down"]:
            score += 20
        if breakout["bullish_breakout_retest"] or breakout["bearish_breakout_retest"]:
            score += 10
        if sweep["sweep_high"] or sweep["sweep_low"]:
            score += 10

        return {
            "structure_bias": structure_bias,
            "score": score,
            "bos": bos,
            "liquidity_sweep": sweep,
            "breakout_retest": breakout,
            "swings": swings,
        }