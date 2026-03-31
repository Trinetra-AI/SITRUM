# app/upgrades/pro_runner.py

from pprint import pprint

from app.core.data_fetcher import DataFetcher
from app.core.timeframe_manager import TimeframeManager
from app.core.indicator_engine import IndicatorEngine
from app.core.session_engine import SessionEngine
from app.core.macro_filter_engine import MacroFilterEngine
from app.core.signal_generator import SignalGenerator

from app.upgrades.market_regime_engine import MarketRegimeEngine
from app.upgrades.pro_trend_engine import ProTrendEngine
from app.upgrades.pro_structure_engine import ProStructureEngine
from app.upgrades.pro_zone_engine import ProZoneEngine
from app.upgrades.pro_momentum_engine import ProMomentumEngine
from app.upgrades.pro_confluence_engine import ProConfluenceEngine
from app.upgrades.pro_explanation_engine import ProExplanationEngine


class SirtumAIPro:
    def __init__(self):
        self.fetcher = DataFetcher()

    def enrich_all_timeframes(self, data_map: dict) -> dict:
        enriched = {}
        for tf, df in data_map.items():
            enriched[tf] = IndicatorEngine(df).enrich()
        return enriched

    def analyze(self) -> dict:
        raw_data = self.fetcher.get_all_timeframes()
        tf_manager = TimeframeManager(raw_data)

        validation = tf_manager.validate_alignment()
        if not validation["is_valid"]:
            return {
                "status": "error",
                "message": "Timeframe data validation failed.",
                "details": validation,
            }

        data_map = self.enrich_all_timeframes(raw_data)
        tf_manager = TimeframeManager(data_map)

        df_15m = tf_manager.get_primary()
        df_1h = tf_manager.get_confirmation()
        df_4h = tf_manager.get_bias()

        latest_15m = df_15m.iloc[-1]
        latest_price = float(latest_15m["close"])
        latest_atr = float(latest_15m["atr"]) if "atr" in latest_15m and latest_15m["atr"] == latest_15m["atr"] else 1.0
        current_time = latest_15m["time"]

        trend_15m = ProTrendEngine(df_15m).analyze()
        trend_1h = ProTrendEngine(df_1h).analyze()
        trend_4h = ProTrendEngine(df_4h).analyze()

        structure_15m = ProStructureEngine(df_15m).analyze()
        zone_15m = ProZoneEngine(df_15m).analyze()
        momentum_15m = ProMomentumEngine(df_15m).analyze()
        session_15m = SessionEngine(df_15m).analyze()
        market_regime_15m = MarketRegimeEngine(df_15m).analyze()

        macro_result = MacroFilterEngine(current_time=current_time).analyze()

        confluence_result = ProConfluenceEngine(
            trend_15m=trend_15m,
            trend_1h=trend_1h,
            trend_4h=trend_4h,
            structure_15m=structure_15m,
            zone_15m=zone_15m,
            momentum_15m=momentum_15m,
            session_15m=session_15m,
            macro_result=macro_result,
            market_regime_15m=market_regime_15m,
            latest_price=latest_price,
            latest_atr=latest_atr,
        ).analyze()

        signal_result = SignalGenerator(confluence_result).generate()

        explanation = ProExplanationEngine(
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

        return {
            "status": "success",
            "mode": "PRO",
            "symbol": "XAU/USD",
            "timestamp": str(current_time),
            "latest_price": latest_price,
            "signal_result": signal_result,
            "explanation": explanation,
            "trend": {"15m": trend_15m, "1h": trend_1h, "4h": trend_4h},
            "structure": {"15m": structure_15m},
            "zones": {"15m": zone_15m},
            "momentum": {"15m": momentum_15m},
            "session": {"15m": session_15m},
            "market_regime": {"15m": market_regime_15m},
            "macro": macro_result,
            "confluence": confluence_result,
            "validation": validation,
        }

    def pretty_print_result(self, result: dict):
        if result["status"] != "success":
            print("\n❌ SIRTUM AI PRO ERROR")
            pprint(result)
            return

        signal = result["signal_result"]

        print("\n" + "=" * 60)
        print("             SIRTUM AI — PRO MODE")
        print("=" * 60)
        print(f"Mode         : {result['mode']}")
        print(f"Symbol       : {result['symbol']}")
        print(f"Timestamp    : {result['timestamp']}")
        print(f"Last Price   : {round(result['latest_price'], 2)}")
        print("-" * 60)
        print(f"Signal       : {signal['signal']}")
        print(f"Confidence   : {signal['confidence']}% ({signal['grade']})")
        print(f"Entry        : {signal['entry']}")
        print(f"Stop Loss    : {signal['stop_loss']}")
        print(f"Target       : {signal['target']}")
        print(f"Risk/Reward  : {signal['risk_reward']}")
        print("-" * 60)
        print("Explanation:")
        print(result["explanation"])
        print("=" * 60 + "\n")