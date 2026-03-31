# app/core/signal_generator.py

from app.config import ROUND_PRICE


class SignalGenerator:
    def __init__(self, confluence_result: dict):
        self.confluence_result = confluence_result

    def generate(self) -> dict:
        signal = self.confluence_result["signal"]
        rr = self.confluence_result["rr_result"]
        confidence = self.confluence_result["confidence"]

        if signal == "NO TRADE":
            return {
                "signal": "NO TRADE",
                "entry": None,
                "stop_loss": None,
                "target": None,
                "risk_reward": None,
                "confidence": confidence["confidence"],
                "grade": confidence["grade"],
            }

        return {
            "signal": signal,
            "entry": round(rr["entry"], ROUND_PRICE),
            "stop_loss": round(rr["stop_loss"], ROUND_PRICE),
            "target": round(rr["target"], ROUND_PRICE),
            "risk_reward": round(rr["rr"], 2),
            "confidence": confidence["confidence"],
            "grade": confidence["grade"],
        }