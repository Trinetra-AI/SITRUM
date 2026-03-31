# app/core/data_fetcher.py

import pandas as pd
from pathlib import Path
from typing import Dict

from app.config import (
    REQUIRED_OHLC_COLUMNS,
    SUPPORTED_TIMEFRAMES,
    DEFAULT_ANALYSIS_BARS,
)
from app.utils.time_utils import ensure_datetime_utc


class DataFetcher:
    def __init__(self):
        self.supported_timeframes = SUPPORTED_TIMEFRAMES

    def load_csv(self, filepath: Path, bars: int = DEFAULT_ANALYSIS_BARS) -> pd.DataFrame:
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")

        df = pd.read_csv(filepath)

        missing = [col for col in REQUIRED_OHLC_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in {filepath.name}: {missing}")

        df = ensure_datetime_utc(df, "time")
        df = df.dropna(subset=["time", "open", "high", "low", "close"]).copy()

        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

        df = df.dropna(subset=["open", "high", "low", "close"])
        df = df.sort_values("time").reset_index(drop=True)

        if bars and len(df) > bars:
            df = df.tail(bars).reset_index(drop=True)

        return df

    def get_timeframe_data(self, timeframe: str, bars: int = DEFAULT_ANALYSIS_BARS) -> pd.DataFrame:
        if timeframe not in self.supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        return self.load_csv(self.supported_timeframes[timeframe], bars=bars)

    def get_all_timeframes(self, bars: int = DEFAULT_ANALYSIS_BARS) -> Dict[str, pd.DataFrame]:
        return {
            tf: self.get_timeframe_data(tf, bars=bars)
            for tf in self.supported_timeframes.keys()
        }