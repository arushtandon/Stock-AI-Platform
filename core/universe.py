"""
Stock, index, and multi-asset universe definitions.
Target: US, European, Japanese, Hong Kong equities + commodities (Brent, Gold, Silver, Bitcoin).
"""
from pathlib import Path
from typing import List

# Major US indices
MAJOR_INDICES = [
    "SPX",
    "NDX",
    "DJI",
    "RUT",
]

# US equities (representative large names)
DEFAULT_US_SYMBOLS: List[str] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V",
    "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "PYPL", "BAC", "XOM",
    "CVX", "ADBE", "NFLX", "CRM", "PEP", "KO", "ABT", "COST", "AVGO", "TMO",
    "ACN", "DHR", "NEE", "CSCO", "INTC", "AMD", "QCOM", "TXN", "INTU", "AMGN",
    "HON", "AMAT", "IBM", "ORCL", "LOW", "SBUX", "GE", "CAT", "DE",
    "AXP", "BLK", "GS", "MS", "C", "SPGI", "PLD", "GILD", "LMT", "RTX",
    "BA", "UPS", "PM", "MDT", "BMY", "ADI", "CVS", "SYK", "ISRG", "REGN",
    "COIN", "UBER", "ABNB", "SHOP", "SQ", "ROKU", "CRWD", "PANW", "SNOW", "MDB",
]

# European equities (yfinance: .DE Xetra, .PA Paris, .AS Amsterdam, .L London, .SW Swiss)
EUROPEAN_SYMBOLS: List[str] = [
    "SAP.DE", "ALV.DE", "SIE.DE", "DTE.DE", "VNA.DE", "MBG.DE", "ADS.DE", "BAS.DE", "BAYN.DE", "ALLIANZ.DE",
    "OR.PA", "MC.PA", "SAN.PA", "AIR.PA", "SU.PA", "FP.PA", "DSY.PA", "BNP.PA", "ENGI.PA", "VIV.PA",
    "ASML.AS", "PHIA.AS", "HEIA.AS", "AD.AS", "UNA.AS", "INGA.AS", "KPN.AS",
    "HSBA.L", "SHEL.L", "AZN.L", "ULVR.L", "GSK.L", "DGE.L", "RIO.L", "BP.L", "NG.L", "REL.L",
    "NOVN.SW", "ROG.SW", "NESN.SW", "NOVOB.SW", "UBSG.SW", "SREN.SW",
]

# Japanese equities (yfinance: .T Tokyo)
JAPANESE_SYMBOLS: List[str] = [
    "7203.T", "6758.T", "6861.T", "9984.T", "8306.T", "9432.T", "8035.T", "8058.T", "6902.T", "7267.T",
    "9983.T", "4519.T", "6098.T", "6367.T", "6501.T", "6954.T", "7974.T", "8031.T", "8058.T", "9433.T",
]

# Hong Kong equities (yfinance: .HK)
HONG_KONG_SYMBOLS: List[str] = [
    "0700.HK", "9988.HK", "0941.HK", "1299.HK", "3690.HK", "2318.HK", "2382.HK", "2628.HK", "0939.HK", "1398.HK",
    "3988.HK", "1810.HK", "2269.HK", "9618.HK", "9961.HK", "9999.HK",
]

# Commodities and crypto (yfinance symbols)
COMMODITY_SYMBOLS: List[str] = [
    "BZ=F",   # Brent crude
    "GC=F",   # Gold
    "SI=F",   # Silver
    "BTC-USD", # Bitcoin
]

# Combined global universe (no BRK.B to avoid yfinance issues)
DEFAULT_UNIVERSE_SYMBOLS: List[str] = (
    DEFAULT_US_SYMBOLS
    + EUROPEAN_SYMBOLS
    + JAPANESE_SYMBOLS
    + HONG_KONG_SYMBOLS
    + COMMODITY_SYMBOLS
)

UNIVERSE_FILE = Path(__file__).parent.parent / "data" / "universe.csv"


def get_universe_symbols(limit: int = 3000) -> List[str]:
    """Return list of symbols to analyze: from CSV if present, else default global universe."""
    if UNIVERSE_FILE.exists():
        lines = UNIVERSE_FILE.read_text(encoding="utf-8").strip().split("\n")
        symbols = [line.split(",")[0].strip() for line in lines[1:] if line]
        if symbols:
            return symbols[:limit]
    return DEFAULT_UNIVERSE_SYMBOLS[:limit]
