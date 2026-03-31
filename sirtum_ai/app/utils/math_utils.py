# app/utils/math_utils.py

import numpy as np
import pandas as pd


def rolling_slope(series: pd.Series, window: int = 5) -> pd.Series:
    """
    Returns rolling slope of a series using simple linear regression.
    """
    slopes = [np.nan] * len(series)

    for i in range(window - 1, len(series)):
        y = series.iloc[i - window + 1:i + 1].values
        x = np.arange(window)

        if np.isnan(y).any():
            slopes[i] = np.nan
            continue

        m, _ = np.polyfit(x, y, 1)
        slopes[i] = m

    return pd.Series(slopes, index=series.index)


def zscore(series: pd.Series, window: int = 20) -> pd.Series:
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std


def distance(a: float, b: float) -> float:
    return abs(a - b)


def percent_change(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return ((b - a) / a) * 100.0


def candle_body(open_price: float, close_price: float) -> float:
    return abs(close_price - open_price)


def candle_range(high: float, low: float) -> float:
    return abs(high - low)


def body_ratio(open_price: float, high: float, low: float, close_price: float) -> float:
    rng = candle_range(high, low)
    if rng == 0:
        return 0.0
    return candle_body(open_price, close_price) / rng


def upper_wick(open_price: float, high: float, close_price: float) -> float:
    return high - max(open_price, close_price)


def lower_wick(open_price: float, low: float, close_price: float) -> float:
    return min(open_price, close_price) - low


def wick_ratio(open_price: float, high: float, low: float, close_price: float) -> dict:
    body = candle_body(open_price, close_price)
    if body == 0:
        body = 0.0001

    return {
        "upper_wick_to_body": upper_wick(open_price, high, close_price) / body,
        "lower_wick_to_body": lower_wick(open_price, low, close_price) / body,
    }