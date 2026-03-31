# app/core/confidence_engine.py

from app.config import (
    WEIGHT_HTF_TREND,
    WEIGHT_MTF_ALIGNMENT,
    WEIGHT_STRUCTURE,
    WEIGHT_ZONE,
    WEIGHT_MOMENTUM,
    WEIGHT_SESSION,
    WEIGHT_MACRO,
    WEIGHT_RR,
)


class ConfidenceEngine:
    def __init__(
        self,
        htf_trend_score: float,
        mtf_alignment_score: float,
        structure_score: float,
        zone_score: float,
        momentum_score: float,
        session_score: float,
        macro_score: float,
        rr_score: float,
    ):
        self.htf_trend_score = htf_trend_score
        self.mtf_alignment_score = mtf_alignment_score
        self.structure_score = structure_score
        self.zone_score = zone_score
        self.momentum_score = momentum_score
        self.session_score = session_score
        self.macro_score = macro_score
        self.rr_score = rr_score

    def calculate(self) -> dict:
        weighted_score = (
            (self.htf_trend_score / 100) * WEIGHT_HTF_TREND +
            (self.mtf_alignment_score / 100) * WEIGHT_MTF_ALIGNMENT +
            (self.structure_score / 100) * WEIGHT_STRUCTURE +
            (self.zone_score / 100) * WEIGHT_ZONE +
            (self.momentum_score / 100) * WEIGHT_MOMENTUM +
            (self.session_score / 100) * WEIGHT_SESSION +
            (self.macro_score / 100) * WEIGHT_MACRO +
            (self.rr_score / 100) * WEIGHT_RR
        )

        confidence = round(weighted_score, 2)

        if confidence >= 80:
            quality = "A+"
        elif confidence >= 70:
            quality = "A"
        elif confidence >= 60:
            quality = "B"
        elif confidence >= 50:
            quality = "C"
        else:
            quality = "D"

        return {
            "confidence": confidence,
            "grade": quality,
        }