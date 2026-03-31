# app/utils/candle_utils.py

import pandas as pd
from app.utils.math_utils import body_ratio, wick_ratio


def is_bullish_candle(row: pd.Series) -> bool:
    return row["close"] > row["open"]


def is_bearish_candle(row: pd.Series) -> bool:
    return row["close"] < row["open"]


def candle_direction(row: pd.Series) -> str:
    if row["close"] > row["open"]:
        return "bullish"
    elif row["close"] < row["open"]:
        return "bearish"
    return "neutral"


def get_candle_stats(row: pd.Series) -> dict:
    wr = wick_ratio(row["open"], row["high"], row["low"], row["close"])
    return {
        "direction": candle_direction(row),
        "body_ratio": body_ratio(row["open"], row["high"], row["low"], row["close"]),
        "upper_wick_to_body": wr["upper_wick_to_body"],
        "lower_wick_to_body": wr["lower_wick_to_body"],
    }


def recent_candle_strength(df: pd.DataFrame, lookback: int = 3) -> dict:
    if len(df) < lookback:
        return {
            "bullish_count": 0,
            "bearish_count": 0,
            "dominant_side": "neutral"
        }

    recent = df.tail(lookback)
    bullish = sum(recent["close"] > recent["open"])
    bearish = sum(recent["close"] < recent["open"])

    if bullish > bearish:
        dominant = "bullish"
    elif bearish > bullish:
        dominant = "bearish"
    else:
        dominant = "neutral"

    return {
        "bullish_count": bullish,
        "bearish_count": bearish,
        "dominant_side": dominant
    }