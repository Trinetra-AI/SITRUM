# app/core/explanation_engine.py


class ExplanationEngine:
    def __init__(
        self,
        signal_result: dict,
        trend_15m: dict,
        trend_1h: dict,
        trend_4h: dict,
        structure_15m: dict,
        zone_15m: dict,
        momentum_15m: dict,
        session_15m: dict,
        confluence_result: dict,
    ):
        self.signal_result = signal_result
        self.trend_15m = trend_15m
        self.trend_1h = trend_1h
        self.trend_4h = trend_4h
        self.structure_15m = structure_15m
        self.zone_15m = zone_15m
        self.momentum_15m = momentum_15m
        self.session_15m = session_15m
        self.confluence_result = confluence_result

    def build(self) -> str:
        signal = self.signal_result["signal"]
        confidence = self.signal_result["confidence"]
        grade = self.signal_result["grade"]
        macro = self.confluence_result["macro_result"]
        rr = self.confluence_result["rr_result"]

        parts = []

        parts.append(
            f"4H trend is {self.trend_4h['trend']}, 1H trend is {self.trend_1h['trend']}, and 15m trend is {self.trend_15m['trend']}."
        )

        parts.append(
            f"Intraday structure currently shows {self.structure_15m['structure_bias']} conditions with a structure score of {self.structure_15m['score']}."
        )

        parts.append(
            f"Momentum reads {self.momentum_15m['momentum']} while the current session is {self.session_15m['session']} ({self.session_15m['session_quality']})."
        )

        parts.append(
            f"Price is currently {self.zone_15m['price_location'].replace('_', ' ')} based on the detected support/resistance zone."
        )

        if macro["blocked"]:
            parts.append(f"Macro filter warning: {macro['reason']}")

        if signal == "NO TRADE":
            if macro["blocked"]:
                parts.append("The setup is blocked mainly due to macro event risk.")
            elif rr["is_rr_valid"] is False:
                parts.append("The setup was rejected because the current risk/reward is not good enough.")
            else:
                parts.append("The setup does not meet the minimum confluence threshold required for a valid trade.")
        else:
            parts.append(
                f"The AI favors a {signal} setup with confidence {confidence}% ({grade}) and estimated RR of {round(rr['rr'], 2)}."
            )

        return " ".join(parts)