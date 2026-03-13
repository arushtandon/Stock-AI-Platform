"""
Stock and index universe definitions.
Target: 3000+ global stocks + major index constituents.
"""
from pathlib import Path
from typing import List

# Major US indices and representative constituents (expand via data file)
MAJOR_INDICES = [
    "SPX",   # S&P 500
    "NDX",   # NASDAQ 100
    "DJI",   # Dow Jones Industrial Average
    "RUT",   # Russell 2000
]

# Example large universe - in production load from DB or CSV
DEFAULT_UNIVERSE_SYMBOLS: List[str] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "JPM", "V",
    "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "PYPL", "BAC", "XOM",
    "CVX", "ADBE", "NFLX", "CRM", "PEP", "KO", "ABT", "COST", "AVGO", "TMO",
    "ACN", "DHR", "NEE", "CSCO", "INTC", "AMD", "QCOM", "TXN", "INTU", "AMGN",
    "HON", "AMAT", "IBM", "ORCL", "LOW", "SBUX", "GE", "CAT", "DE", "MMC",
    "AXP", "BLK", "GS", "MS", "C", "SPGI", "PLD", "GILD", "LMT", "RTX",
    "BA", "UPS", "PM", "MDT", "BMY", "ADI", "CVS", "SYK", "ISRG", "REGN",
    "ZTS", "CI", "SO", "DUK", "BDX", "EOG", "SLB", "MO", "CL", "APD",
    "MMM", "ITW", "APTV", "ECL", "AON", "CME", "SCHW", "CB", "PGR", "MET",
    "AIG", "AFL", "TRP", "PSA", "EQIX", "KLAC", "SNPS", "CDNS", "MCHP",
    "NXPI", "MRVL", "FTNT", "PANW", "CRWD", "DDOG", "SNOW", "MDB", "NET",
    "ZM", "DOCU", "SHOP", "SQ", "ROKU", "UBER", "LYFT", "ABNB", "DASH",
    "COIN", "HOOD", "RBLX", "U", "PATH", "PLTR", "AI", "SMCI",
]

UNIVERSE_FILE = Path(__file__).parent.parent / "data" / "universe.csv"


def get_universe_symbols(limit: int = 3000) -> List[str]:
    """Return list of symbols to analyze. In production, load from DB/CSV."""
    if UNIVERSE_FILE.exists():
        lines = UNIVERSE_FILE.read_text(encoding="utf-8").strip().split("\n")
        symbols = [line.split(",")[0].strip() for line in lines[1:] if line]
        return symbols[:limit]
    return DEFAULT_UNIVERSE_SYMBOLS[:limit]
