# run.py

import json
from app.main import SirtumAI


def pretty_print_result(result: dict):
    print("\n" + "=" * 70)
    print(" " * 24 + "SIRTUM AI ANALYSIS")
    print("=" * 70)

    if result["status"] != "success":
        print("STATUS:", result["status"])
        print("MESSAGE:", result.get("message", "Unknown error"))
        print("DETAILS:", json.dumps(result.get("details", {}), indent=2))
        print("=" * 70)
        return

    signal = result["signal_result"]

    print(f"Market        : {result['market']}")
    print(f"Timestamp     : {result['timestamp']}")
    print(f"Latest Price  : {round(result['latest_price'], 2)}")
    print("-" * 70)

    print(f"Signal        : {signal['signal']}")
    print(f"Confidence    : {signal['confidence']}% ({signal['grade']})")
    print(f"Entry         : {signal['entry']}")
    print(f"Stop Loss     : {signal['stop_loss']}")
    print(f"Target        : {signal['target']}")
    print(f"Risk/Reward   : {signal['risk_reward']}")
    print("-" * 70)

    print("Explanation:")
    print(result["explanation"])
    print("-" * 70)

    print("Trend Summary:")
    print(f"15m Trend     : {result['analysis']['trend_15m']['trend']}")
    print(f"1H Trend      : {result['analysis']['trend_1h']['trend']}")
    print(f"4H Trend      : {result['analysis']['trend_4h']['trend']}")
    print("-" * 70)

    print("Market Context:")
    print(f"Structure     : {result['analysis']['structure_15m']['structure_bias']}")
    print(f"Momentum      : {result['analysis']['momentum_15m']['momentum']}")
    print(f"Session       : {result['analysis']['session_15m']['session']}")
    print(f"Macro Blocked : {result['analysis']['macro_result']['blocked']}")
    print("-" * 70)

    print("JSON Snapshot (short):")
    short_json = {
        "signal_result": result["signal_result"],
        "timestamp": result["timestamp"],
        "latest_price": result["latest_price"],
    }
    print(json.dumps(short_json, indent=2))

    print("=" * 70 + "\n")


if __name__ == "__main__":
    ai = SirtumAI()
    result = ai.run_analysis()
    pretty_print_result(result)