# app/upgrades/validation_engine.py

from app.upgrades.pro_config import (
    NO_TRADE_IF_SIDEWAYS,
    NO_TRADE_IF_WEAK_BREAKOUT,
    NO_TRADE_IF_LOW_SESSION_AND_WEAK_MOMENTUM,
)


class ValidationEngine:
    def __init__(
        self,
        trend_15m: dict,
        trend_1h: dict,
        structure_15m: dict,
        momentum_15m: dict,
        session_15m: dict,
        market_regime_15m: dict,
    ):
        self.trend_15m = trend_15m
        self.trend_1h = trend_1h
        self.structure_15m = structure_15m
        self.momentum_15m = momentum_15m
        self.session_15m = session_15m
        self.market_regime_15m = market_regime_15m

    def analyze(self) -> dict:
        blockers = []

        if NO_TRADE_IF_SIDEWAYS:
            if "sideways" in self.trend_15m["trend"] or self.market_regime_15m["regime"] == "tight_range":
                blockers.append("Market is sideways or trapped in a tight range.")

        if NO_TRADE_IF_WEAK_BREAKOUT:
            bo = self.structure_15m.get("breakout_retest", {})
            if not bo.get("bullish_breakout_retest", False) and not bo.get("bearish_breakout_retest", False):
                blockers.append("No valid breakout-retest confirmation detected.")

        if NO_TRADE_IF_LOW_SESSION_AND_WEAK_MOMENTUM:
            weak_momentum = self.momentum_15m["momentum"] in ["weak", "neutral"]
            weak_session = self.session_15m["session_quality"] == "low_activity"
            if weak_momentum and weak_session:
                blockers.append("Weak momentum during low-quality session.")

        valid = len(blockers) == 0

        return {
            "valid": valid,
            "blockers": blockers,
            "score": 85 if valid else 25,
        }