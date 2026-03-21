"""
Qullamaggie Momentum Breakout Scanner & Trade Execution System
Alpaca Paper Trading | Full Spec Implementation
"""

import os
import math
import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf
from tabulate import tabulate

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIGURATION — adjust thresholds here without touching logic
# ─────────────────────────────────────────────────────────────
CONFIG = {
    # Universe filters
    "min_price": 3.0,
    "min_market_cap": 10_000_000,
    "min_avg_dollar_vol": 500_000,
    "min_adr_pct": 5.0,

    # Momentum qualification
    "min_move_21d": 30.0,
    "min_move_63d": 30.0,

    # MA structure
    "ma_tolerance_pct": 3.0,       # how close out-of-order MAs can be
    "ma_slope_10_lookback": 3,     # days back for SMA10 slope check
    "ma_slope_20_lookback": 3,     # days back for SMA20 slope check
    "ma_slope_50_lookback": 7,     # days back for SMA50 slope check
    "extended_from_50_pct": 50.0,  # above this → penalise score

    # Consolidation
    "consol_min_days": 3,
    "consol_max_days": 42,
    "consol_sweet_min": 10,
    "consol_sweet_max": 25,
    "consol_max_range_pct": 30.0,  # max consolidation range
    "consol_tight_pct": 15.0,      # tight flag (high quality)
    "consol_reasonable_pct": 25.0, # reasonable tight
    "tightening_tolerance": 1.1,   # second half ≤ first half * this
    "higher_lows_tolerance": 0.98, # 2% tolerance on higher lows
    "surfing_tolerance": 0.97,     # close must not be below SMA20 * this
    "vol_dry_ideal": 0.60,         # below this → best vol dry-up
    "vol_dry_pass": 0.80,          # above this → lower quality

    # Breakout / entry
    "orb_minutes": 5,              # opening range bar width in minutes
    "min_vol_projection_pass": 1.5,
    "min_vol_projection_ideal": 2.0,
    "breakout_candle_expansion": 1.25,  # today_range ≥ avg_consol_range * this
    "spy_sma50_tolerance": 0.97,        # SPY can be 3% below SMA50
    "weak_market_size_factor": 0.50,    # reduce position 50% in weak market

    # Position sizing
    "risk_pct": 0.005,             # 0.5% of equity per trade
    "max_position_pct": 0.30,      # hard cap: 30% of equity per trade

    # Trade management
    "partial_exit_day": 3,         # take partial after this many days
    "partial_exit_frac": 0.40,     # sell 40% at partial
    "early_partial_r_multiple": 2.0,  # take partial early at 2R
    "trail_ma": 10,                # default trailing MA period
    "trail_ma_fast": 20,           # slower trail option

    # Credentials (override via env)
    "api_key": os.getenv("ALPACA_API_KEY", "PKJ237IFEHIRMP700WGNZCULD4"),
    "secret_key": os.getenv("ALPACA_SECRET_KEY", "DV9oHCLAriBqFqbSDK5pnaSzLKfSabaAg8BX8qRnvymh"),
    "base_url": "https://paper-api.alpaca.markets",

    # Scanner universe — fetch from Alpaca or use a predefined list
    "use_sp500_universe": True,    # True = scan S&P500; False = use symbol_list below
    "symbol_list": [],             # custom list if use_sp500_universe == False
    "max_symbols": 200,            # cap for scan (API rate limit safety)
}

ET = ZoneInfo("America/New_York")


# ─────────────────────────────────────────────────────────────
# SECTION 1 — ADR%
# ─────────────────────────────────────────────────────────────
def compute_adr(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Average Daily Range %: mean of 100 * (High/Low - 1) over `period` days."""
    daily_adr = 100 * ((df["High"] / df["Low"]) - 1)
    return daily_adr.rolling(window=period).mean()


# ─────────────────────────────────────────────────────────────
# SECTION 2 — UNIVERSE / DATA FETCH
# ─────────────────────────────────────────────────────────────
def get_alpaca_client():
    """Return an initialised Alpaca TradingClient (paper)."""
    from alpaca.trading.client import TradingClient
    return TradingClient(
        api_key=CONFIG["api_key"],
        secret_key=CONFIG["secret_key"],
        paper=True,
    )


def get_alpaca_data_client():
    """Return an initialised Alpaca StockHistoricalDataClient."""
    from alpaca.data.historical import StockHistoricalDataClient
    return StockHistoricalDataClient(
        api_key=CONFIG["api_key"],
        secret_key=CONFIG["secret_key"],
    )


def fetch_tradable_symbols() -> list:
    """
    Return full US common stock universe (~6,600 symbols).
    Loads from cached workspace file first, falls back to Nasdaq API.
    """
    workspace_cache = "/root/.openclaw/workspace/us_universe.txt"
    if os.path.exists(workspace_cache):
        with open(workspace_cache) as f:
            symbols = [l.strip() for l in f if l.strip()]
        print(f"[UNIVERSE] Loaded {len(symbols)} symbols from workspace cache")
        return symbols

    # Live fetch from Nasdaq screener
    print("[UNIVERSE] Fetching from Nasdaq screener API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nasdaq.com/",
    }
    import requests as req_lib
    all_syms = []
    for exchange in ["nasdaq", "nyse", "amex"]:
        url = (f"https://api.nasdaq.com/api/screener/stocks"
               f"?tableonly=true&limit=5000&offset=0&exchange={exchange}&download=true")
        try:
            r = req_lib.get(url, headers=headers, timeout=20)
            rows = r.json().get("data", {}).get("rows", [])
            for row in rows:
                sym = row.get("symbol", "").strip()
                if sym and sym.isalpha() and 1 <= len(sym) <= 5:
                    all_syms.append(sym)
        except Exception as e:
            print(f"  [WARN] {exchange}: {e}")
    symbols = sorted(set(all_syms))
    with open(workspace_cache, "w") as f:
        f.write("\n".join(symbols))
    print(f"[UNIVERSE] {len(symbols)} symbols fetched and cached")
    return symbols


def get_sp500_symbols() -> list:
    """Scrape S&P 500 constituent list from Wikipedia."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0]
        symbols = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        return symbols
    except Exception as e:
        print(f"[WARN] Could not fetch S&P500 list: {e}. Using fallback symbols.")
        return []


def fetch_bars(symbol: str, days: int = 200) -> pd.DataFrame:
    """
    Fetch daily OHLCV bars for `symbol` going back `days` calendar days.
    Uses yfinance for reliability and simplicity.
    Returns a DataFrame with columns: Open, High, Low, Close, Volume
    """
    end = datetime.now(ET)
    start = end - timedelta(days=days + 60)  # extra buffer for weekends/holidays
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), interval="1d")
        if df.empty:
            return pd.DataFrame()
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.dropna(inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


def fetch_intraday_bars(symbol: str, minutes: int = 5) -> pd.DataFrame:
    """
    Fetch intraday bars for today's session via Alpaca.
    Returns DataFrame with columns: Open, High, Low, Close, Volume, timestamp
    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

    client = get_alpaca_data_client()

    now = datetime.now(ET)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)

    tf = TimeFrame(minutes, TimeFrameUnit.Minute)
    req = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=tf,
        start=market_open,
        end=now,
    )
    try:
        bars = client.get_stock_bars(req)
        df = bars.df
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
        df.columns = ["timestamp", "Open", "High", "Low", "Close", "Volume"]
        return df
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# SECTION 2 — UNIVERSE FILTERS
# ─────────────────────────────────────────────────────────────

# Known biotech/pharma symbols to skip (fast exclusion without API call)
KNOWN_BIOTECH = {
    "MRNA","BNTX","REGN","BIIB","GILD","VRTX","ALNY","SGEN","BMRN","EXEL",
    "RARE","FOLD","ACAD","INCY","IONS","SAGE","ARNA","PTCT","BLUE","EDIT",
    "NTLA","BEAM","CRSP","FATE","KYMR","RCUS","XNCR","ARVN","KRTX","PRAX",
    "ABBV","LLY","PFE","JNJ","AZN","RHHBY","NVS","SNY","GSK","BMY",
    "MRK","AMGN","CELG","ALXN","JAZZ","ENDP","SUPN","NKTR","HALO","ACOR",
}

def is_biotech(symbol: str, info_cache: dict = None) -> bool:
    """
    Return True if stock is a biotech/pharma.
    Fast path: check KNOWN_BIOTECH set first.
    Falls back to cached yfinance info if available.
    """
    if symbol in KNOWN_BIOTECH:
        return True
    excluded_industries = {"Biotechnology", "Drug Manufacturers", "Pharmaceutical", "Pharmaceuticals"}
    if info_cache and symbol in info_cache:
        info = info_cache[symbol]
        sector = info.get("sector", "")
        industry = info.get("industry", "")
        if sector == "Healthcare" and industry in excluded_industries:
            return True
    return False


def filter_universe(symbols: list) -> list:
    """
    Apply Section 2 hard filters to a list of symbols.
    Returns list of (symbol, df) tuples that pass all filters.
    Batches yfinance downloads for speed.
    """
    qualified = []
    total = min(len(symbols), CONFIG["max_symbols"])
    print(f"[SCAN] Downloading bars for {total} symbols (batched)...")

    # Batch download all symbols at once — much faster than one-by-one
    batch_syms = [s for s in symbols[:total] if s not in KNOWN_BIOTECH]
    try:
        raw = yf.download(
            tickers=" ".join(batch_syms),
            period="1y",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        print(f"[WARN] Batch download failed: {e} — falling back to individual fetches")
        raw = None

    for i, sym in enumerate(batch_syms):
        if i % 25 == 0:
            print(f"  ... {i}/{len(batch_syms)}")

        # Extract this symbol's bars from batch or fetch individually
        try:
            if raw is not None and sym in raw.columns.get_level_values(0):
                df = raw[sym].copy()
                df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            else:
                df = fetch_bars(sym, days=200)
        except Exception:
            df = fetch_bars(sym, days=200)

        if df is None or len(df) < 65:
            continue

        # 2.3 Price >= $3
        last_close = df["Close"].iloc[-1]
        if last_close < CONFIG["min_price"]:
            continue

        # 2.5 Average daily dollar volume >= $500k
        avg_dollar_vol = (df["Close"] * df["Volume"]).rolling(20).mean().iloc[-1]
        if avg_dollar_vol < CONFIG["min_avg_dollar_vol"]:
            continue

        # 2.6 ADR% >= 5%
        adr_series = compute_adr(df)
        if pd.isna(adr_series.iloc[-1]) or adr_series.iloc[-1] < CONFIG["min_adr_pct"]:
            continue

        qualified.append((sym, df))

    print(f"[SCAN] Universe filter: {len(qualified)} symbols passed out of {len(batch_syms)} scanned.")
    return qualified


# ─────────────────────────────────────────────────────────────
# SECTION 3 — MOMENTUM QUALIFICATION
# ─────────────────────────────────────────────────────────────
def check_momentum(df: pd.DataFrame) -> tuple:
    """
    Returns (passes: bool, move_21d: float, move_63d: float, sector_for_ranking: str)
    Stock must have >= 30% gain in last 21 OR 63 trading days.
    """
    if len(df) < 65:
        return False, 0.0, 0.0

    move_21d = (df["Close"].iloc[-1] - df["Close"].iloc[-22]) / df["Close"].iloc[-22] * 100
    move_63d = (df["Close"].iloc[-1] - df["Close"].iloc[-64]) / df["Close"].iloc[-64] * 100

    passes = move_21d >= CONFIG["min_move_21d"] or move_63d >= CONFIG["min_move_63d"]
    return passes, round(move_21d, 2), round(move_63d, 2)


def rank_sectors(qualified_stocks: list) -> dict:
    """
    Section 3.3: Group by sector, rank by average 63-day return.
    Returns {symbol: sector_bonus (0 or 1)}.
    """
    sector_returns = {}
    sym_sectors = {}

    for sym, df in qualified_stocks:
        try:
            sector = yf.Ticker(sym).info.get("sector", "Unknown")
        except Exception:
            sector = "Unknown"
        sym_sectors[sym] = sector
        move_63d = (df["Close"].iloc[-1] - df["Close"].iloc[-64]) / df["Close"].iloc[-64] * 100
        if sector not in sector_returns:
            sector_returns[sector] = []
        sector_returns[sector].append(move_63d)

    # Average return per sector
    sector_avg = {s: sum(v) / len(v) for s, v in sector_returns.items()}
    top2_sectors = sorted(sector_avg, key=sector_avg.get, reverse=True)[:2]

    bonuses = {}
    for sym, _ in qualified_stocks:
        bonuses[sym] = 1 if sym_sectors.get(sym) in top2_sectors else 0
    return bonuses


# ─────────────────────────────────────────────────────────────
# SECTION 4 — MA STRUCTURE
# ─────────────────────────────────────────────────────────────
def check_ma_structure(df: pd.DataFrame) -> tuple:
    """
    Returns (passes: bool, distance_from_50_pct: float)
    Validates SMA10/20/50 stack, direction, and price-above-MA rules.
    """
    if len(df) < 55:
        return False, 0.0

    closes = df["Close"]
    sma10 = closes.rolling(10).mean()
    sma20 = closes.rolling(20).mean()
    sma50 = closes.rolling(50).mean()

    s10 = sma10.iloc[-1]
    s20 = sma20.iloc[-1]
    s50 = sma50.iloc[-1]
    price = closes.iloc[-1]
    tol = CONFIG["ma_tolerance_pct"] / 100

    # 4.2 MA stack with tolerance
    sma10_vs_20_ok = (s10 > s20) or (abs(s10 - s20) / s20 <= tol)
    sma20_vs_50_ok = (s20 > s50) or (abs(s20 - s50) / s50 <= tol)
    if not (sma10_vs_20_ok and sma20_vs_50_ok):
        return False, 0.0

    # 4.3 MA slope — all must be rising or flat
    lb10 = CONFIG["ma_slope_10_lookback"]
    lb20 = CONFIG["ma_slope_20_lookback"]
    lb50 = CONFIG["ma_slope_50_lookback"]
    if len(sma10) < lb10 + 1 or len(sma50) < lb50 + 1:
        return False, 0.0

    slope10_ok = sma10.iloc[-1] >= sma10.iloc[-(lb10 + 1)]
    slope20_ok = sma20.iloc[-1] >= sma20.iloc[-(lb20 + 1)]
    slope50_ok = sma50.iloc[-1] >= sma50.iloc[-(lb50 + 1)]
    if not (slope10_ok and slope20_ok and slope50_ok):
        return False, 0.0

    # 4.4 Price above all MAs
    if not (price > s10 and price > s20 and price > s50):
        return False, 0.0

    distance_from_50 = (price - s50) / s50 * 100
    return True, round(distance_from_50, 2)


# ─────────────────────────────────────────────────────────────
# SECTION 5 — CONSOLIDATION DETECTION
# ─────────────────────────────────────────────────────────────
def detect_consolidation(df: pd.DataFrame) -> tuple:
    """
    Returns:
        (found: bool, N: int, consolidation_high: float, consolidation_low: float, quality_metrics: dict)

    quality_metrics keys:
        consolidation_range_pct, volume_ratio, higher_lows, tightening,
        consol_days, surfing_ok
    """
    if len(df) < 50:
        return False, 0, 0, 0, {}

    closes = df["Close"]
    highs = df["High"]
    lows = df["Low"]
    volume = df["Volume"]
    sma20 = closes.rolling(20).mean()

    # Find local peak: most recent 10-day rolling high maximum
    roll10_high = highs.rolling(10).max()
    # Look back up to consol_max_days + 5 to find the peak
    lookback = CONFIG["consol_max_days"] + 5
    recent_slice = roll10_high.iloc[-lookback:]
    if recent_slice.empty:
        return False, 0, 0, 0, {}

    # Find the index of the most recent maximum in the rolling-high window
    # We want the last date where the rolling high was at its highest (the peak)
    peak_idx_pos = recent_slice.argmax()   # position in recent_slice
    # Convert to position from the end of df
    N = len(recent_slice) - 1 - peak_idx_pos  # days from peak to last bar (exclusive)

    N = min(N, CONFIG["consol_max_days"])

    if N < CONFIG["consol_min_days"]:
        return False, 0, 0, 0, {}

    # 5.3 Consolidation range (exclude today = iloc[-1])
    consol_highs = highs.iloc[-N:-1]
    consol_lows = lows.iloc[-N:-1]
    consol_closes = closes.iloc[-N:-1]
    consol_vol = volume.iloc[-N:-1]
    consol_sma20 = sma20.iloc[-N:-1]

    if consol_highs.empty:
        return False, 0, 0, 0, {}

    consolidation_high = consol_highs.max()
    consolidation_low = consol_lows.min()
    consolidation_range_pct = (consolidation_high - consolidation_low) / consolidation_low * 100

    if consolidation_range_pct >= CONFIG["consol_max_range_pct"]:
        return False, N, consolidation_high, consolidation_low, {}

    # 5.4 Tightening range — split in half
    half = len(consol_highs) // 2
    if half < 1:
        tightening = True  # too short to split — assume ok
        tightening_ideal = False
    else:
        first_half_range = (highs.iloc[-N:-N + half] - lows.iloc[-N:-N + half]).mean()
        second_half_range = (highs.iloc[-N + half:-1] - lows.iloc[-N + half:-1]).mean()
        tightening = second_half_range <= first_half_range * CONFIG["tightening_tolerance"]
        tightening_ideal = second_half_range < first_half_range

    # 5.5 Higher lows — split into thirds
    third = max(1, N // 3)
    tol = CONFIG["higher_lows_tolerance"]
    try:
        low_first = lows.iloc[-N:-N + third].min()
        low_second = lows.iloc[-N + third:-N + 2 * third].min()
        low_third = lows.iloc[-N + 2 * third:-1].min()
        higher_lows = (low_third >= low_second * tol) and (low_second >= low_first * tol)
    except Exception:
        higher_lows = False

    # 5.6 Surfing the 20-SMA — no close more than 3% below SMA20
    surfing_ok = True
    for i in range(-N, -1):
        try:
            if closes.iloc[i] < sma20.iloc[i] * CONFIG["surfing_tolerance"]:
                surfing_ok = False
                break
        except Exception:
            pass

    # 5.7 Volume dry-up
    baseline_start = -N - 20
    baseline_end = -N
    if -baseline_start > len(volume):
        baseline_vol = volume.mean()
    else:
        baseline_vol = volume.iloc[baseline_start:baseline_end].mean()

    avg_consol_vol = consol_vol.mean() if not consol_vol.empty else baseline_vol
    volume_ratio = avg_consol_vol / baseline_vol if baseline_vol > 0 else 1.0

    quality_metrics = {
        "consolidation_range_pct": round(consolidation_range_pct, 2),
        "volume_ratio": round(volume_ratio, 3),
        "higher_lows": higher_lows,
        "tightening": tightening,
        "tightening_ideal": tightening_ideal if half >= 1 else False,
        "consol_days": N,
        "surfing_ok": surfing_ok,
        "baseline_vol": baseline_vol,
        "avg_consol_range": (consol_highs - consol_lows).mean() if not consol_highs.empty else 0,
    }

    return True, N, consolidation_high, consolidation_low, quality_metrics


# ─────────────────────────────────────────────────────────────
# SECTION 6 — SETUP QUALITY SCORE
# ─────────────────────────────────────────────────────────────
def compute_setup_score(quality_metrics: dict, distance_from_50: float, sector_bonus: int) -> int:
    """Returns an integer score 0–10 based on quality metrics."""
    score = 0
    rng = quality_metrics.get("consolidation_range_pct", 100)
    vol_ratio = quality_metrics.get("volume_ratio", 1.0)
    higher_lows = quality_metrics.get("higher_lows", False)
    tightening_ideal = quality_metrics.get("tightening_ideal", False)
    N = quality_metrics.get("consol_days", 0)

    if rng < CONFIG["consol_tight_pct"]:
        score += 2  # very tight base
    elif rng < CONFIG["consol_reasonable_pct"]:
        score += 1  # reasonably tight

    if vol_ratio < CONFIG["vol_dry_ideal"]:
        score += 2  # strong volume dry-up
    elif vol_ratio < CONFIG["vol_dry_pass"]:
        score += 1  # moderate dry-up

    if higher_lows:
        score += 1

    if tightening_ideal:
        score += 1

    score += sector_bonus  # +1 if in top 2 sectors

    if CONFIG["consol_sweet_min"] <= N <= CONFIG["consol_sweet_max"]:
        score += 1  # sweet-spot consolidation duration

    if distance_from_50 > CONFIG["extended_from_50_pct"]:
        score -= 1  # price too extended from 50-SMA

    return max(0, score)


# ─────────────────────────────────────────────────────────────
# SECTION 7 — BREAKOUT ENTRY
# ─────────────────────────────────────────────────────────────
def check_market_conditions() -> tuple:
    """
    Returns (market_ok: bool, spy_close: float, spy_sma50: float)
    SPY must be within 3% of its 50-SMA.
    """
    df = fetch_bars("SPY", days=80)
    if df.empty or len(df) < 51:
        return True, 0.0, 0.0  # benefit of doubt
    spy_sma50 = df["Close"].rolling(50).mean().iloc[-1]
    spy_close = df["Close"].iloc[-1]
    market_ok = spy_close >= spy_sma50 * CONFIG["spy_sma50_tolerance"]
    return market_ok, round(spy_close, 2), round(spy_sma50, 2)


def check_breakout_entry(df: pd.DataFrame, symbol: str,
                          consolidation_high: float,
                          quality_metrics: dict) -> tuple:
    """
    Returns (breakout_triggered: bool, entry_price: float, stop_price: float,
             breakout_level: float, skip_reason: str)

    Checks ORB, ADR gate, volume confirmation, and range expansion.
    Falls back to EOD scan if market is closed.
    """
    breakout_level = consolidation_high
    adr_pct = compute_adr(df).iloc[-1]
    skip_reason = ""

    # Try intraday bars (works during market hours)
    intraday = fetch_intraday_bars(symbol, minutes=CONFIG["orb_minutes"])
    now_et = datetime.now(ET)
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_is_open = now_et.hour >= 9 and (now_et.hour < 16) and now_et.weekday() < 5

    if not intraday.empty and market_is_open:
        # ORB: first 5-min candle
        orb_candle = intraday.iloc[0]
        orb_high = orb_candle["High"]
        orb_low = orb_candle["Low"]
        day_low = intraday["Low"].min()

        # Current price = last close in intraday bars
        current_price = intraday["Close"].iloc[-1]
        current_volume = intraday["Volume"].sum()
        minutes_elapsed = max(1, (now_et - market_open_time).seconds // 60)
        projected_vol = current_volume / (minutes_elapsed / 390)
        baseline_vol = quality_metrics.get("baseline_vol", 1)

        # 7.2 Breakout trigger
        triggered = current_price > orb_high and current_price > breakout_level

        # 7.3 ADR gate — don't chase
        adr_absolute = df["Close"].iloc[-2] * (adr_pct / 100)
        max_entry_price = day_low + adr_absolute
        if current_price > max_entry_price:
            return False, 0, 0, breakout_level, "missed — too extended"

        # 7.4 Volume confirmation
        vol_multiple = projected_vol / baseline_vol if baseline_vol > 0 else 0
        if vol_multiple < CONFIG["min_vol_projection_pass"]:
            return False, 0, 0, breakout_level, "low volume breakout — skip"

        # 7.5 Range expansion on breakout candle
        today_range = intraday["High"].max() - intraday["Low"].min()
        avg_consol_range = quality_metrics.get("avg_consol_range", 0)
        if avg_consol_range > 0 and today_range < avg_consol_range * CONFIG["breakout_candle_expansion"]:
            # Not a hard block — lower quality, note it
            skip_reason = "weak range expansion"

        if triggered:
            entry_price = current_price
            stop_price = orb_low  # stop = ORB candle low (9.2)
            return True, round(entry_price, 4), round(stop_price, 4), breakout_level, skip_reason
        else:
            return False, 0, 0, breakout_level, "no breakout yet"

    else:
        # EOD / offline scan: check if yesterday's close was above breakout level
        last_close = df["Close"].iloc[-1]
        if last_close > breakout_level:
            return True, round(last_close, 4), round(df["Low"].iloc[-1], 4), breakout_level, "EOD signal — entry at next open"
        return False, 0, 0, breakout_level, "not yet breaking out"


# ─────────────────────────────────────────────────────────────
# SECTION 8 — POSITION SIZING
# ─────────────────────────────────────────────────────────────
def get_account_equity() -> float:
    """Fetch current equity from Alpaca paper account."""
    try:
        client = get_alpaca_client()
        account = client.get_account()
        return float(account.equity)
    except Exception as e:
        print(f"[ACCOUNT] Auth error — {e}")
        return 0.0


def compute_position_size(account_equity: float, entry: float, stop: float) -> int:
    """
    Returns number of shares to buy based on risk % of equity.
    Caps at 30% of account in any single position.
    """
    risk_per_share = entry - stop
    if risk_per_share <= 0:
        return 0  # malformed — skip

    dollar_risk = account_equity * CONFIG["risk_pct"]
    raw_shares = math.floor(dollar_risk / risk_per_share)

    max_position_value = account_equity * CONFIG["max_position_pct"]
    max_shares_by_cap = math.floor(max_position_value / entry)

    return min(raw_shares, max_shares_by_cap)


# ─────────────────────────────────────────────────────────────
# SECTION 10 — TRADE MANAGEMENT
# ─────────────────────────────────────────────────────────────
def manage_open_positions(open_positions: list, daily_bars: dict) -> list:
    """
    For each open position, check:
    - Partial exit at 3–5 days or 2R
    - Move stop to breakeven after partial
    - Trail with SMA10 on daily close

    open_positions: list of dicts with keys:
        symbol, entry_price, stop_price, shares, entry_date, partial_taken

    Returns updated positions list with any sell orders submitted.
    """
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce

    client = get_alpaca_client()
    today = pd.Timestamp.now(tz="UTC").normalize()
    updated = []

    for pos in open_positions:
        sym = pos["symbol"]
        df = daily_bars.get(sym)
        if df is None or df.empty:
            updated.append(pos)
            continue

        entry = pos["entry_price"]
        stop = pos["stop_price"]
        shares = pos["shares"]
        entry_date = pd.Timestamp(pos["entry_date"], tz="UTC")
        partial_taken = pos.get("partial_taken", False)

        # Trading days held (approximate)
        days_held = (today - entry_date).days * 5 // 7

        current_close = df["Close"].iloc[-1]
        sma10 = df["Close"].rolling(10).mean().iloc[-1]

        # 10.4 Trail with SMA10 — exit if CLOSE < SMA10
        if current_close < sma10:
            print(f"[TRADE MGMT] {sym}: close {current_close:.2f} < SMA10 {sma10:.2f} → EXIT trailing stop")
            try:
                order_req = MarketOrderRequest(
                    symbol=sym,
                    qty=shares,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                )
                client.submit_order(order_req)
                print(f"[TRADE MGMT] {sym}: sell order submitted for {shares} shares (trail exit)")
            except Exception as e:
                print(f"[TRADE MGMT] {sym}: order error: {e}")
            continue  # position closed — don't add back

        # 10.2 Partial exit trigger
        risk_per_share = entry - stop
        unrealized_gain = (current_close - entry) * shares

        early_partial_threshold = CONFIG["early_partial_r_multiple"] * risk_per_share * shares
        should_take_partial = (
            not partial_taken and (
                days_held >= CONFIG["partial_exit_day"] and current_close > entry
                or unrealized_gain > early_partial_threshold
            )
        )

        if should_take_partial:
            sell_qty = math.floor(shares * CONFIG["partial_exit_frac"])
            if sell_qty > 0:
                print(f"[TRADE MGMT] {sym}: taking partial — selling {sell_qty}/{shares} shares")
                try:
                    order_req = MarketOrderRequest(
                        symbol=sym,
                        qty=sell_qty,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY,
                    )
                    client.submit_order(order_req)
                    pos["shares"] = shares - sell_qty
                    pos["stop_price"] = entry  # 10.3 move stop to breakeven
                    pos["partial_taken"] = True
                    print(f"[TRADE MGMT] {sym}: stop moved to breakeven {entry:.2f}")
                except Exception as e:
                    print(f"[TRADE MGMT] {sym}: partial order error: {e}")

        updated.append(pos)

    return updated


# ─────────────────────────────────────────────────────────────
# ENTRY EXECUTION
# ─────────────────────────────────────────────────────────────
def submit_entry_order(symbol: str, shares: int, market_ok: bool) -> bool:
    """Submit a market buy order via Alpaca. Reduces size in weak market."""
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce

    if shares <= 0:
        print(f"[ORDER] {symbol}: 0 shares computed — skip")
        return False

    # Weak market → halve position
    if not market_ok:
        shares = max(1, math.floor(shares * CONFIG["weak_market_size_factor"]))
        print(f"[ORDER] {symbol}: weak market — reduced to {shares} shares")

    client = get_alpaca_client()
    try:
        order_req = MarketOrderRequest(
            symbol=symbol,
            qty=shares,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        # Note: use OrderSide.BUY for real entries — using SELL would be wrong
        # Corrected below:
        order_req = MarketOrderRequest(
            symbol=symbol,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        order = client.submit_order(order_req)
        print(f"[ORDER] {symbol}: BUY {shares} shares submitted — order ID {order.id}")
        return True
    except Exception as e:
        print(f"[ORDER] {symbol}: order failed — {e}")
        return False


# ─────────────────────────────────────────────────────────────
# MAIN SCANNER
# ─────────────────────────────────────────────────────────────
def run_scanner(auto_trade: bool = False) -> list:
    """
    Orchestrates the full scan:
    1. Build universe
    2. Apply hard filters
    3. Momentum qualification
    4. MA structure
    5. Consolidation detection
    6. Score and rank
    7. (Optional) submit breakout entries

    Returns list of result dicts for qualified setups.
    """
    print("\n" + "=" * 70)
    print("  QULLAMAGGIE BREAKOUT SCANNER")
    print(f"  {datetime.now(ET).strftime('%Y-%m-%d %H:%M ET')}")
    print("=" * 70)

    # Check market conditions once
    market_ok, spy_close, spy_sma50 = check_market_conditions()
    status = "✅ OK" if market_ok else "⚠️  WEAK"
    print(f"\n[MARKET] SPY: {spy_close} | SMA50: {spy_sma50} | Status: {status}")

    # Build symbol universe
    if CONFIG["use_sp500_universe"]:
        symbols = get_sp500_symbols()
        if not symbols:
            print("[WARN] S&P500 list empty — loading full US universe")
            symbols = fetch_tradable_symbols()
        if not symbols:
            print("[WARN] Full universe unavailable — using built-in extended watchlist")
            # Last-resort hardcoded list
            symbols = [
                "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AVGO","AMD","ORCL",
                "CRM","ADBE","INTC","QCOM","TXN","MU","AMAT","LRCX","KLAC","SNPS",
                "CDNS","MRVL","NXPI","ON","STX","WDC","SWKS","QRVO","MPWR","ENTG",
                "JPM","GS","MS","BAC","C","WFC","BLK","SCHW","AXP","V","MA","PYPL",
                "SQ","COIN","ICE","CME","SPGI","MCO","TFC","USB","PNC","COF",
                "UNH","JNJ","LLY","ABBV","MRK","TMO","ABT","DHR","SYK","BSX",
                "EW","ZBH","RMD","ISRG","MDT","BAX","BDX","ZTS","IDXX","A",
                "XOM","CVX","COP","EOG","SLB","HAL","PSX","VLO","MPC","OXY",
                "PXD","DVN","FANG","HES","MRO","APA","BKR","NOV","WHD","CIVI",
                "HD","LOW","TGT","COST","WMT","AMZN","TJX","ROST","DG","DLTR",
                "NKE","LULU","TPR","RL","PVH","VFC","HBI","UAA","SKX","CROX",
                "NEE","DUK","SO","D","AEP","EXC","SRE","XEL","WEC","ETR",
                "PLD","AMT","CCI","EQIX","SPG","O","VICI","DLR","PSA","EQR",
                "DE","CAT","RTX","HON","GE","MMM","EMR","ETN","PH","ROK",
                "LMT","BA","NOC","GD","HII","LHX","TDG","HWM","SPR","KTOS",
                "UBER","LYFT","ABNB","BKNG","EXPE","TRIP","DASH","DKNG","PENN","CZR",
                "NFLX","DIS","WBD","PARA","CMCSA","T","VZ","TMUS","CHTR","DISH",
                "SHOP","MELI","SE","GLOB","WIX","MNDY","BILL","HUBS","DDOG","CRWD",
                "ZS","PANW","FTNT","OKTA","S","TENB","RPM","VRNS","CYBR","QLYS",
                "NOW","SNOW","PLTR","MDB","ESTC","SPLK","SUMO","DT","FSLY","NET",
                "ZM","DOCU","DOCN","GTLB","BRZE","AFRM","SOFI","UPST","LC","OPEN",
                "GME","AMC","BBBY","BBAI","MULN","CLOV","WISH","SPCE","NKLA","RIDE",
                "ENPH","SEDG","FSLR","CSIQ","NOVA","ARRY","MAXN","SPWR","HASI","AES",
                "ALB","LTHM","SQM","PLL","LAC","SGML","LICY","MP","NMG","NOVS",
                "FCX","NEM","GOLD","AEM","KGC","WPM","AG","PAAS","CDE","SILV",
                "CLF","X","NUE","STLD","RS","CMC","TS","TMST","MT","ARCH",
                "CF","MOS","NTR","IPI","FMC","CE","EMN","HUN","OLN","LYB",
                "TSCO","SFM","KR","SYY","US","PFGC","CHEF","SPTN","WEIS","GO",
            ]
    elif CONFIG["symbol_list"]:
        symbols = CONFIG["symbol_list"]
    else:
        # Try Alpaca, fall back to the extended list
        try:
            symbols = fetch_tradable_symbols()
        except Exception:
            print("[WARN] Alpaca asset fetch failed — using built-in list")
            symbols = get_sp500_symbols() or []

    print(f"[SCAN] Starting universe: {len(symbols)} symbols")

    # Step 1: Hard universe filters (Section 2)
    qualified_universe = filter_universe(symbols)

    # Step 2: Momentum check (Section 3)
    momentum_passed = []
    for sym, df in qualified_universe:
        passes, m21, m63 = check_momentum(df)
        if passes:
            momentum_passed.append((sym, df, m21, m63))

    print(f"[SCAN] Momentum filter: {len(momentum_passed)} symbols passed")

    # Step 3: Sector bonus scoring
    sector_bonuses = rank_sectors([(s, d) for s, d, _, _ in momentum_passed])

    # Step 4: MA structure + consolidation
    results = []
    ma_failed = []
    consol_failed = []
    for sym, df, m21, m63 in momentum_passed:
        ma_ok, dist50 = check_ma_structure(df)
        if not ma_ok:
            ma_failed.append(sym)
            continue

        consol_ok, N, consol_high, consol_low, qm = detect_consolidation(df)
        if not consol_ok or not qm:
            consol_failed.append(f"{sym}(no_base)")
            continue

        # Surfing check
        if not qm.get("surfing_ok", True):
            consol_failed.append(f"{sym}(surf_viol)")
            continue

        score = compute_setup_score(qm, dist50, sector_bonuses.get(sym, 0))
        adr_val = round(compute_adr(df).iloc[-1], 2)

        results.append({
            "symbol": sym,
            "score": score,
            "consol_days": N,
            "adr_pct": adr_val,
            "dist_from_50": dist50,
            "consol_range_pct": qm["consolidation_range_pct"],
            "vol_ratio": qm["volume_ratio"],
            "breakout_level": round(consol_high, 4),
            "move_21d": m21,
            "move_63d": m63,
            "higher_lows": qm["higher_lows"],
            "tightening": qm["tightening"],
            "df": df,
            "quality_metrics": qm,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"[SCAN] Passed momentum filter: {[s for s,_,_,_ in momentum_passed]}")
    print(f"[SCAN] Failed MA structure: {ma_failed}")
    print(f"[SCAN] Failed consolidation: {consol_failed}")
    print(f"[SCAN] Full qualification: {len(results)} setups found\n")

    # Print ranked watchlist table
    if results:
        table_data = []
        for r in results:
            table_data.append([
                r["symbol"],
                r["score"],
                f"{r['consol_days']}d",
                f"{r['adr_pct']}%",
                f"{r['dist_from_50']}%",
                f"{r['consol_range_pct']}%",
                f"{r['vol_ratio']:.2f}x",
                f"${r['breakout_level']:.2f}",
                "✓" if r["higher_lows"] else "✗",
                "✓" if r["tightening"] else "✗",
            ])

        headers = [
            "Symbol", "Score", "Consol", "ADR%",
            "Dist50%", "ConsolRange%", "VolRatio",
            "BreakoutLevel", "HiLows", "Tighten"
        ]
        print(tabulate(table_data, headers=headers, tablefmt="rounded_outline"))
    else:
        print("[SCAN] No qualifying setups found today.")

    # Optional: auto-submit breakout entries for top setups
    if auto_trade and results:
        try:
            equity = get_account_equity()
            print(f"\n[ACCOUNT] Equity: ${equity:,.2f}")
        except Exception as e:
            print(f"[ACCOUNT] Could not fetch equity: {e}")
            equity = 0

        if equity > 0:
            for r in results[:5]:  # top 5 setups only
                sym = r["symbol"]
                triggered, entry, stop, bl, reason = check_breakout_entry(
                    r["df"], sym, r["breakout_level"], r["quality_metrics"]
                )
                if triggered and not reason.startswith("missed"):
                    shares = compute_position_size(equity, entry, stop)
                    print(f"\n[ENTRY] {sym}: entry={entry} stop={stop} shares={shares} | {reason}")
                    submit_entry_order(sym, shares, market_ok)
                else:
                    print(f"[SKIP] {sym}: {reason}")

    return results


def run_trade_manager():
    """
    Manages existing open positions.
    Loads positions from Alpaca account and applies Section 10 rules.
    """
    print("\n" + "=" * 70)
    print("  TRADE MANAGER")
    print("=" * 70)

    client = get_alpaca_client()
    try:
        alpaca_positions = client.get_all_positions()
    except Exception as e:
        print(f"[TRADE MGMT] Could not fetch positions: {e}")
        return

    if not alpaca_positions:
        print("[TRADE MGMT] No open positions.")
        return

    print(f"[TRADE MGMT] {len(alpaca_positions)} open positions found")

    # Build daily bars cache
    daily_bars = {}
    for pos in alpaca_positions:
        df = fetch_bars(pos.symbol, days=60)
        if not df.empty:
            daily_bars[pos.symbol] = df

    # Convert Alpaca positions to our internal format
    open_positions = []
    for pos in alpaca_positions:
        open_positions.append({
            "symbol": pos.symbol,
            "entry_price": float(pos.avg_entry_price),
            "stop_price": float(pos.avg_entry_price) * 0.95,  # fallback: 5% stop
            "shares": int(pos.qty),
            "entry_date": str(pd.Timestamp.now(tz="UTC").date()),  # approximation
            "partial_taken": False,
        })

    manage_open_positions(open_positions, daily_bars)


# ─────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Qullamaggie Breakout Scanner")
    parser.add_argument("--trade", action="store_true", help="Auto-submit breakout entries")
    parser.add_argument("--manage", action="store_true", help="Run trade manager only")
    args = parser.parse_args()

    if args.manage:
        run_trade_manager()
    else:
        results = run_scanner(auto_trade=args.trade)
        if args.trade:
            run_trade_manager()
