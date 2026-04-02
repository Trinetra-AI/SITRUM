from pathlib import Path
import pandas as pd
import yfinance as yf

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def normalize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()

    # Detect time column
    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "time"})
    elif "Date" in df.columns:
        df = df.rename(columns={"Date": "time"})

    # Standardize OHLCV
    rename_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=rename_map)

    required = ["time", "open", "high", "low", "close"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column after normalization: {col}")

    if "volume" not in df.columns:
        df["volume"] = 0

    df = df[["time", "open", "high", "low", "close", "volume"]].copy()
    df["time"] = pd.to_datetime(df["time"], utc=True)

    return df.sort_values("time").reset_index(drop=True)


def save_csv(df: pd.DataFrame, filename: str):
    filepath = RAW_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"Saved: {filepath}")


def fetch_gold_data():
    print("Downloading XAU/USD proxy data...")

    # Gold futures proxy from Yahoo Finance
    ticker = "GC=F"

    # 15-minute data (recent intraday)
    df_15m = yf.download(
        ticker,
        interval="15m",
        period="60d",
        auto_adjust=False,
        progress=False
    )
    df_15m = normalize_ohlc(df_15m)
    save_csv(df_15m, "xauusd_15m.csv")

    # 1-hour data
    df_1h = yf.download(
        ticker,
        interval="60m",
        period="730d",
        auto_adjust=False,
        progress=False
    )
    df_1h = normalize_ohlc(df_1h)
    save_csv(df_1h, "xauusd_1h.csv")

    # 4-hour data (build from 1h)
    df_1h["time"] = pd.to_datetime(df_1h["time"], utc=True)
    df_4h = (
        df_1h.set_index("time")
        .resample("4h")
        .agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        })
        .dropna()
        .reset_index()
    )
    save_csv(df_4h, "xauusd_4h.csv")

    print("\nAll raw XAU/USD files created successfully.")


if __name__ == "__main__":
    fetch_gold_data()