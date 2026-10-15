"""Approved feature descriptions; no new indicator definitions or tuned parameters."""

FEATURES = {
    "M1": "log(hour close/open) / max(RMS60, fitted hourly floor); normalized, not raw return",
    "M2": "previous 20 origin-matched mature 4h-return mean / floored RMS60; origin-specific",
    "M3": "previous-session-locked 5-day log momentum / (sqrt(5) × floored daily RMS63)",
    "M4": "older log(C[d−21]/C[d−126]) / (sqrt(105) × floored daily RMS63)",
    "V1": "log(max(hourly RMS12, fitted hourly floor))",
    "V2": "log(max(hourly RMS60, fitted hourly floor))",
    "V3": "V1 − V2; log short/long volatility ratio",
    "B1": "log(hourly high/low)",
    "B2": "(2C−H−L)/(H−L), bounded [−1,1]; genuine zero range gives0 plus quality flag",
    "Q1": "log same-slot volume / prior20 matching-session mean, with fitted pseudocount",
    "Q2": "log(prior5 full-session mean volume / prior60 mean), fitted pseudocounts",
    "T1": "log(current hourly close / previous20 daily-close SMA); not raw SMA",
    "T2": "mean sign of preceding20 daily close returns, native [−1,1]",
    "T3": "(EMA6−EMA18)/current hourly close; normalized DIF, not MACD histogram",
    "T4": "(EMA24−EMA72)/current hourly close; normalized EMA difference",
    "T5": "(Wilder RSI14−50)/50, native [−1,1]; includes genuine overnight close changes",
}
MARKET = {
    "U1": "SPY completed-hour log(C/O) / floored hourly RMS60",
    "U2": "log floored absolute SPY hourly RMS60",
    "U3": "log floored SPY RMS12/RMS60",
    "U4": "previous-session-locked SPY 5-day momentum / (sqrt(5) × daily RMS63)",
    "U5": "previous-session-locked SPY 20-day momentum / (sqrt(20) × daily RMS63)",
}
