# app/core/risk_reward_engine.py

from app.config import MIN_RR, PREFERRED_RR, MAX_STOP_ATR, MIN_STOP_ATR


class RiskRewardEngine:
    def __init__(self, current_price: float, atr: float):
        self.current_price = current_price
        self.atr = atr if atr and atr > 0 else 1.0

    def build_buy_setup(self, support: float, resistance: float) -> dict:
        entry = self.current_price
        stop = support - (self.atr * 0.3)
        target = resistance

        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr = reward / risk if risk > 0 else 0

        return {
            "side": "BUY",
            "entry": entry,
            "stop_loss": stop,
            "target": target,
            "risk": risk,
            "reward": reward,
            "rr": rr,
        }

    def build_sell_setup(self, support: float, resistance: float) -> dict:
        entry = self.current_price
        stop = resistance + (self.atr * 0.3)
        target = support

        risk = abs(stop - entry)
        reward = abs(entry - target)
        rr = reward / risk if risk > 0 else 0

        return {
            "side": "SELL",
            "entry": entry,
            "stop_loss": stop,
            "target": target,
            "risk": risk,
            "reward": reward,
            "rr": rr,
        }

    def evaluate(self, setup: dict) -> dict:
        stop_atr = setup["risk"] / self.atr if self.atr > 0 else 0
        rr = setup["rr"]

        is_rr_valid = rr >= MIN_RR
        is_stop_valid = MIN_STOP_ATR <= stop_atr <= MAX_STOP_ATR

        if is_rr_valid and rr >= PREFERRED_RR and is_stop_valid:
            quality = "excellent"
            score = 90
        elif is_rr_valid and is_stop_valid:
            quality = "acceptable"
            score = 75
        elif not is_rr_valid:
            quality = "poor_rr"
            score = 35
        elif not is_stop_valid:
            quality = "bad_stop_distance"
            score = 30
        else:
            quality = "weak"
            score = 40

        return {
            **setup,
            "stop_atr": round(stop_atr, 2),
            "is_rr_valid": is_rr_valid,
            "is_stop_valid": is_stop_valid,
            "quality": quality,
            "score": score,
        }