# app/upgrades/pro_confluence_engine.py

from app.config import MIN_CONFIDENCE_FOR_SIGNAL
from app.core.risk_reward_engine import RiskRewardEngine
from app.core.confidence_engine import ConfidenceEngine
from app.upgrades.validation_engine import ValidationEngine


class ProConfluenceEngine:
    def __init__(
        self,
        trend_15m: dict,
        trend_1h: dict,
        trend_4h: dict,
        structure_15m: dict,
        zone_15m: dict,
        momentum_15m: dict,
        session_15m: dict,
        macro_result: dict,
        market_regime_15m: dict,
        latest_price: float,
        latest_atr: float,
    ):
        self.trend_15m = trend_15m
        self.trend_1h = trend_1h
        self.trend_4h = trend_4h
        self.structure_15m = structure_15m
        self.zone_15m = zone_15m
        self.momentum_15m = momentum_15m
        self.session_15m = session_15m
        self.macro_result = macro_result
        self.market_regime_15m = market_regime_15m
        self.latest_price = latest_price
        self.latest_atr = latest_atr

    def get_directional_bias(self) -> str:
        t15 = self.trend_15m["trend"]
        t1h = self.trend_1h["trend"]
        t4h = self.trend_4h["trend"]
        s15 = self.structure_15m["structure_bias"]
        m15 = self.momentum_15m["momentum"]

        bullish_votes = 0
        bearish_votes = 0

        for value in [t15, t1h, t4h, s15, m15]:
            val = str(value).lower()
            if "bullish" in val:
                bullish_votes += 1
            if "bearish" in val:
                bearish_votes += 1

        if bullish_votes >= 4 and bullish_votes > bearish_votes:
            return "BUY"
        elif bearish_votes >= 4 and bearish_votes > bullish_votes:
            return "SELL"
        return "NO TRADE"

    def get_mtf_alignment_score(self, side: str) -> float:
        t15 = self.trend_15m["trend"]
        t1h = self.trend_1h["trend"]
        t4h = self.trend_4h["trend"]

        if side == "BUY":
            aligned = sum("bullish" in t.lower() for t in [t15, t1h, t4h])
        elif side == "SELL":
            aligned = sum("bearish" in t.lower() for t in [t15, t1h, t4h])
        else:
            aligned = 0

        return {3: 95, 2: 65, 1: 30, 0: 10}[aligned]

    def build_rr_result(self, side: str) -> dict:
        sr = self.zone_15m["support_resistance"]
        rr_engine = RiskRewardEngine(self.latest_price, self.latest_atr)

        if side == "BUY":
            raw_setup = rr_engine.build_buy_setup(sr["support"], sr["resistance"])
        elif side == "SELL":
            raw_setup = rr_engine.build_sell_setup(sr["support"], sr["resistance"])
        else:
            return {
                "side": "NO TRADE",
                "entry": self.latest_price,
                "stop_loss": None,
                "target": None,
                "risk": 0,
                "reward": 0,
                "rr": 0,
                "stop_atr": 0,
                "is_rr_valid": False,
                "is_stop_valid": False,
                "quality": "none",
                "score": 10,
            }

        return rr_engine.evaluate(raw_setup)

    def analyze(self) -> dict:
        side = self.get_directional_bias()
        rr_result = self.build_rr_result(side)

        validation_result = ValidationEngine(
            trend_15m=self.trend_15m,
            trend_1h=self.trend_1h,
            structure_15m=self.structure_15m,
            momentum_15m=self.momentum_15m,
            session_15m=self.session_15m,
            market_regime_15m=self.market_regime_15m,
        ).analyze()

        if self.macro_result["blocked"]:
            final_signal = "NO TRADE"
        else:
            final_signal = side

        mtf_alignment_score = self.get_mtf_alignment_score(side)
        htf_trend_score = self.trend_4h["score"]

        confidence_engine = ConfidenceEngine(
            htf_trend_score=htf_trend_score,
            mtf_alignment_score=mtf_alignment_score,
            structure_score=self.structure_15m["score"],
            zone_score=self.zone_15m["score"],
            momentum_score=self.momentum_15m["score"],
            session_score=self.session_15m["score"],
            macro_score=self.macro_result["score"],
            rr_score=rr_result["score"],
        )
        confidence_result = confidence_engine.calculate()

        if rr_result["is_rr_valid"] is False:
            final_signal = "NO TRADE"

        if confidence_result["confidence"] < MIN_CONFIDENCE_FOR_SIGNAL:
            final_signal = "NO TRADE"

        if validation_result["valid"] is False:
            final_signal = "NO TRADE"

        return {
            "signal": final_signal,
            "raw_directional_bias": side,
            "confidence": confidence_result,
            "mtf_alignment_score": mtf_alignment_score,
            "rr_result": rr_result,
            "macro_result": self.macro_result,
            "validation_result": validation_result,
            "market_regime": self.market_regime_15m,
        }