# app/core/indicator_engine.py

import numpy as np
import pandas as pd

from app.config import (
    EMA_FAST,
    EMA_MID,
    EMA_SLOW,
    RSI_LENGTH,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    ATR_LENGTH,
    BB_LENGTH,
    BB_STD,
    STOCH_LENGTH,
    STOCH_SMOOTH_K,
    STOCH_SMOOTH_D,
)


class IndicatorEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def add_ema(self):
        self.df[f"ema_{EMA_FAST}"] = self.df["close"].ewm(span=EMA_FAST, adjust=False).mean()
        self.df[f"ema_{EMA_MID}"] = self.df["close"].ewm(span=EMA_MID, adjust=False).mean()
        self.df[f"ema_{EMA_SLOW}"] = self.df["close"].ewm(span=EMA_SLOW, adjust=False).mean()

    def add_rsi(self):
        delta = self.df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        gain = pd.Series(gain, index=self.df.index).rolling(RSI_LENGTH).mean()
        loss = pd.Series(loss, index=self.df.index).rolling(RSI_LENGTH).mean()

        rs = gain / loss.replace(0, np.nan)
        self.df["rsi"] = 100 - (100 / (1 + rs))

    def add_macd(self):
        ema_fast = self.df["close"].ewm(span=MACD_FAST, adjust=False).mean()
        ema_slow = self.df["close"].ewm(span=MACD_SLOW, adjust=False).mean()

        self.df["macd"] = ema_fast - ema_slow
        self.df["macd_signal"] = self.df["macd"].ewm(span=MACD_SIGNAL, adjust=False).mean()
        self.df["macd_hist"] = self.df["macd"] - self.df["macd_signal"]

    def add_atr(self):
        high_low = self.df["high"] - self.df["low"]
        high_close = np.abs(self.df["high"] - self.df["close"].shift())
        low_close = np.abs(self.df["low"] - self.df["close"].shift())

        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.df["atr"] = tr.rolling(ATR_LENGTH).mean()

    def add_bollinger_bands(self):
        ma = self.df["close"].rolling(BB_LENGTH).mean()
        std = self.df["close"].rolling(BB_LENGTH).std()

        self.df["bb_mid"] = ma
        self.df["bb_upper"] = ma + (std * BB_STD)
        self.df["bb_lower"] = ma - (std * BB_STD)

    def add_stochastic(self):
        low_min = self.df["low"].rolling(STOCH_LENGTH).min()
        high_max = self.df["high"].rolling(STOCH_LENGTH).max()

        self.df["stoch_k"] = 100 * ((self.df["close"] - low_min) / (high_max - low_min).replace(0, np.nan))
        self.df["stoch_k"] = self.df["stoch_k"].rolling(STOCH_SMOOTH_K).mean()
        self.df["stoch_d"] = self.df["stoch_k"].rolling(STOCH_SMOOTH_D).mean()

    def enrich(self) -> pd.DataFrame:
        self.add_ema()
        self.add_rsi()
        self.add_macd()
        self.add_atr()
        self.add_bollinger_bands()
        self.add_stochastic()
        return self.df