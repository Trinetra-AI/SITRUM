# app/config.py
from pathlib import Path

# =========================
# BASE PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EVENTS_DIR = DATA_DIR / "events"
MODELS_DIR = DATA_DIR / "models"

# Ensure folders exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# FILE PATHS
# =========================
XAUUSD_15M_FILE = RAW_DATA_DIR / "xauusd_15m.csv"
XAUUSD_1H_FILE = RAW_DATA_DIR / "xauusd_1h.csv"
XAUUSD_4H_FILE = RAW_DATA_DIR / "xauusd_4h.csv"
MACRO_EVENTS_FILE = EVENTS_DIR / "macro_events.csv"

# =========================
# REQUIRED COLUMNS
# =========================
REQUIRED_OHLC_COLUMNS = ["time", "open", "high", "low", "close"]

# =========================
# TIMEFRAMES
# =========================
PRIMARY_TIMEFRAME = "15m"
CONFIRMATION_TIMEFRAME = "1h"
BIAS_TIMEFRAME = "4h"

SUPPORTED_TIMEFRAMES = {
    "15m": XAUUSD_15M_FILE,
    "1h": XAUUSD_1H_FILE,
    "4h": XAUUSD_4H_FILE,
}

# =========================
# INDICATOR SETTINGS
# =========================
EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200

RSI_LENGTH = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

ATR_LENGTH = 14
BB_LENGTH = 20
BB_STD = 2

STOCH_LENGTH = 14
STOCH_SMOOTH_K = 3
STOCH_SMOOTH_D = 3

# =========================
# STRUCTURE SETTINGS
# =========================
SWING_LOOKBACK = 3
BOS_LOOKBACK = 20
LIQUIDITY_SWEEP_WICK_RATIO = 1.5
BREAKOUT_BUFFER = 0.15  # in ATR multiples

# =========================
# ZONE SETTINGS
# =========================
ZONE_LOOKBACK = 50
SR_CLUSTER_TOLERANCE = 1.5  # dollars
RETEST_TOLERANCE_ATR = 0.35

# =========================
# MOMENTUM SETTINGS
# =========================
STRONG_RSI_BULL = 55
STRONG_RSI_BEAR = 45
WEAK_RSI_UPPER = 52
WEAK_RSI_LOWER = 48
STRONG_BODY_RATIO = 0.6
WEAK_BODY_RATIO = 0.3

# =========================
# SESSION SETTINGS (UTC)
# =========================
ASIAN_SESSION = (0, 8)
LONDON_SESSION = (7, 16)
NEW_YORK_SESSION = (13, 22)

# =========================
# MACRO FILTER SETTINGS
# =========================
MACRO_BLOCK_MINUTES_BEFORE = 60
MACRO_BLOCK_MINUTES_AFTER = 30
HIGH_IMPACT_EVENTS = {
    "CPI", "NFP", "FOMC", "FED", "POWELL", "PCE", "GDP", "CPI m/m", "CPI y/y"
}

# =========================
# RISK / REWARD SETTINGS
# =========================
MIN_RR = 1.8
PREFERRED_RR = 2.5
MAX_STOP_ATR = 2.5
MIN_STOP_ATR = 0.4

# =========================
# CONFLUENCE SCORING
# =========================
MIN_CONFIDENCE_FOR_SIGNAL = 60
STRONG_SIGNAL_CONFIDENCE = 75

WEIGHT_HTF_TREND = 20
WEIGHT_MTF_ALIGNMENT = 15
WEIGHT_STRUCTURE = 20
WEIGHT_ZONE = 10
WEIGHT_MOMENTUM = 10
WEIGHT_SESSION = 5
WEIGHT_MACRO = 10
WEIGHT_RR = 10

# =========================
# GENERAL
# =========================
DEFAULT_ANALYSIS_BARS = 300
ROUND_PRICE = 2
ROUND_SCORE = 2