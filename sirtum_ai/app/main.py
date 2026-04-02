# app/main.py
from app.core.data_fetcher import DataFetcher
from app.core.timeframe_manager import TimeframeManager
from app.core.indicator_engine import IndicatorEngine
from app.core.trend_engine import TrendEngine
from app.core.structure_engine import StructureEngine
from app.core.zone_engine import ZoneEngine
from app.core.momentum_engine import MomentumEngine
from app.core.session_engine import SessionEngine
from app.core.macro_filter_engine import MacroFilterEngine
from app.core.confluence_engine import ConfluenceEngine
from app.core.signal_generator import SignalGenerator
from app.core.explanation_engine import ExplanationEngine


class SirtumAI:
    def __init__(self):
        self.fetcher = DataFetcher()

    def _prepare_timeframes(self) -> dict:
        raw_data = self.fetcher.get_all_timeframes()
        enriched_data = {}

        for tf, df in raw_data.items():
            if df is None or df.empty:
                raise ValueError(f"No usable data found for timeframe: {tf}")
            enriched_data[tf] = IndicatorEngine(df).enrich()

        return enriched_data

    def run_analysis(self) -> dict:
        try:
            # =========================
            # LOAD + PREPARE DATA
            # =========================
            data_map = self._prepare_timeframes()

            tfm = TimeframeManager(data_map)
            validation = tfm.validate_alignment()

            if not validation["is_valid"]:
                return {
                    "status": "error",
                    "message": "Timeframe validation failed.",
                    "details": validation,
                }

            df_15m = tfm.get_primary()
            df_1h = tfm.get_confirmation()
            df_4h = tfm.get_bias()

            latest_15m = df_15m.iloc[-1]
            latest_price = float(latest_15m["close"])
            latest_atr = (
                float(latest_15m["atr"])
                if "atr" in latest_15m and latest_15m["atr"] == latest_15m["atr"]
                else 1.0
            )
            current_time = latest_15m["time"]

            # =========================
            # ANALYSIS ENGINES
            # =========================
            trend_15m = TrendEngine(df_15m).analyze()
            trend_1h = TrendEngine(df_1h).analyze()
            trend_4h = TrendEngine(df_4h).analyze()

            structure_15m = StructureEngine(df_15m).analyze()
            zone_15m = ZoneEngine(df_15m).analyze()
            momentum_15m = MomentumEngine(df_15m).analyze()
            session_15m = SessionEngine(df_15m).analyze()
            macro_result = MacroFilterEngine(current_time=current_time).analyze()

            # =========================
            # CONFLUENCE + SIGNAL
            # =========================
            confluence_result = ConfluenceEngine(
                trend_15m=trend_15m,
                trend_1h=trend_1h,
                trend_4h=trend_4h,
                structure_15m=structure_15m,
                zone_15m=zone_15m,
                momentum_15m=momentum_15m,
                session_15m=session_15m,
                macro_result=macro_result,
                latest_price=latest_price,
                latest_atr=latest_atr,
            ).analyze()

            signal_result = SignalGenerator(confluence_result).generate()

            explanation = ExplanationEngine(
                signal_result=signal_result,
                trend_15m=trend_15m,
                trend_1h=trend_1h,
                trend_4h=trend_4h,
                structure_15m=structure_15m,
                zone_15m=zone_15m,
                momentum_15m=momentum_15m,
                session_15m=session_15m,
                confluence_result=confluence_result,
            ).build()

            # =========================
            # FINAL OUTPUT
            # =========================
            return {
                "status": "success",
                "market": "XAU/USD",
                "timestamp": str(current_time),
                "latest_price": latest_price,
                "signal_result": signal_result,
                "explanation": explanation,
                "analysis": {
                    "trend_15m": trend_15m,
                    "trend_1h": trend_1h,
                    "trend_4h": trend_4h,
                    "structure_15m": structure_15m,
                    "zone_15m": zone_15m,
                    "momentum_15m": momentum_15m,
                    "session_15m": session_15m,
                    "macro_result": macro_result,
                    "confluence_result": confluence_result,
                },
                "timeframe_validation": validation,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "details": {"source": "SirtumAI.run_analysis"}
            }