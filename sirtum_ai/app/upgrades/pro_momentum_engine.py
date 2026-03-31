# app/upgrades/pro_momentum_engine.py

import pandas as pd
from app.config import (
    STRONG_RSI_BULL,
    STRONG_RSI_BEAR,
    WEAK_RSI_UPPER,
    WEAK_RSI_LOWER,
    STRONG_BODY_RATIO,
    WEAK_BODY_RATIO,
)
from app.upgrades.pro_config import MOMENTUM_DISPLACEMENT_ATR
from app.utils.candle_utils import get_candle_stats, recent_candle_strength


class ProMomentumEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        latest = self.df.iloc[-1]
        previous = self.df.iloc[-2] if len(self.df) >= 2 else latest

        stats = get_candle_stats(latest)
        recent_strength = recent_candle_strength(self.df, lookback=3)

        rsi = latest["rsi"]
        macd = latest["macd"]
        macd_signal = latest["macd_signal"]
        macd_hist = latest["macd_hist"]
        atr = latest["atr"] if "atr" in latest else 1.0

        candle_displacement = abs(latest["close"] - previous["close"])
        displacement_atr = candle_displacement / atr if atr and atr > 0 else 0

        momentum = "neutral"
        score = 40

        bullish_rsi = rsi >= STRONG_RSI_BULL
        bearish_rsi = rsi <= STRONG_RSI_BEAR

        bullish_macd = macd > macd_signal and macd_hist > 0
        bearish_macd = macd < macd_signal and macd_hist < 0

        strong_bull_candle = stats["direction"] == "bullish" and stats["body_ratio"] >= STRONG_BODY_RATIO
        strong_bear_candle = stats["direction"] == "bearish" and stats["body_ratio"] >= STRONG_BODY_RATIO

        displacement_ok = displacement_atr >= MOMENTUM_DISPLACEMENT_ATR
        weak_candle = stats["body_ratio"] <= WEAK_BODY_RATIO

        if bullish_rsi and bullish_macd and strong_bull_candle and displacement_ok:
            momentum = "bullish_strong"
            score = 90
        elif bearish_rsi and bearish_macd and strong_bear_candle and displacement_ok:
            momentum = "bearish_strong"
            score = 90
        elif rsi > WEAK_RSI_UPPER and macd > macd_signal:
            momentum = "bullish_weak"
            score = 65
        elif rsi < WEAK_RSI_LOWER and macd < macd_signal:
            momentum = "bearish_weak"
            score = 65
        elif weak_candle:
            momentum = "weak"
            score = 35

        return {
            "momentum": momentum,
            "score": score,
            "rsi": float(rsi),
            "macd": float(macd),
            "macd_signal": float(macd_signal),
            "macd_hist": float(macd_hist),
            "displacement_atr": round(displacement_atr, 2),
            "latest_candle": stats,
            "recent_candle_strength": recent_strength,
        }