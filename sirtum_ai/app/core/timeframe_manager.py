# app/core/timeframe_manager.py

from typing import Dict
import pandas as pd

from app.config import PRIMARY_TIMEFRAME, CONFIRMATION_TIMEFRAME, BIAS_TIMEFRAME


class TimeframeManager:
    def __init__(self, data_map: Dict[str, pd.DataFrame]):
        self.data_map = data_map

    def get_primary(self) -> pd.DataFrame:
        return self.data_map[PRIMARY_TIMEFRAME]

    def get_confirmation(self) -> pd.DataFrame:
        return self.data_map[CONFIRMATION_TIMEFRAME]

    def get_bias(self) -> pd.DataFrame:
        return self.data_map[BIAS_TIMEFRAME]

    def get_all(self) -> Dict[str, pd.DataFrame]:
        return self.data_map

    def latest_timestamp_map(self) -> Dict[str, str]:
        result = {}
        for tf, df in self.data_map.items():
            if len(df) == 0:
                result[tf] = None
            else:
                result[tf] = str(df.iloc[-1]["time"])
        return result

    def validate_alignment(self) -> dict:
        """
        Basic sanity check:
        Ensures all timeframes have data and timestamps.
        """
        issues = []

        for tf, df in self.data_map.items():
            if df is None or len(df) == 0:
                issues.append(f"{tf} has no data")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "latest_timestamps": self.latest_timestamp_map()
        }