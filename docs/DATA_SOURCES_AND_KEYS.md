# How to Get Data: Danelfin, Seeking Alpha, Investing.com Pro, TradingView

Below is the **best way to get data** from each source, and what the platform expects.

---

## 1. Danelfin ✅ Official API

**They have an official API and API keys.**

- **Docs:** [danelfin.com/docs/api](https://danelfin.com/docs/api)
- **Pricing:** [danelfin.com/pricing/api](https://danelfin.com/pricing/api) — paid plans (e.g. from ~$52/mo), often with a free trial.
- **How to get a key:** Subscribe to an API plan; they send the key (e.g. by email). Use it in the **`x-api-key`** header.
- **In this app:** Set **`DANELFIN_API_KEY`** in Render (stock-ai-api → Environment). The backend can send it as `x-api-key` when calling `https://apirest.danelfin.com`.
- **Data you get:** AI Score, Fundamental, Technical, Sentiment, Low Risk scores (1–10), US stocks/ETFs.

**Best option:** Use Danelfin’s official API and put the key they give you into `DANELFIN_API_KEY`.

---

## 2. Seeking Alpha — API via RapidAPI

**There is no direct “Seeking Alpha API key” from Seeking Alpha for retail use.** Programmatic access is typically via:

- **RapidAPI – “Seeking Alpha” API:** [rapidapi.com/apidojo/api/seeking-alpha](https://rapidapi.com/apidojo/api/seeking-alpha)  
  You get an **RapidAPI key** (and possibly a subscription to that specific API). That key is used in the request headers when calling the Seeking Alpha API on RapidAPI.
- **Seeking Alpha Premium** (website subscription) gives human access to articles and ratings, but not a standard public API key from Seeking Alpha itself.

**Best option for this app:**  
Use the **Seeking Alpha API on RapidAPI**:

1. Sign up at [rapidapi.com](https://rapidapi.com).
2. Subscribe to the **“Seeking Alpha”** API (e.g. [apidojo/api/seeking-alpha](https://rapidapi.com/apidojo/api/seeking-alpha)).
3. Copy your **RapidAPI key** (sometimes called “X-RapidAPI-Key”).
4. In the backend we can either:
   - Use **`SEEKING_ALPHA_API_KEY`** to store that RapidAPI key and call the Seeking Alpha API on RapidAPI with it, or  
   - Use a dedicated **`RAPIDAPI_KEY`** if we use multiple RapidAPI APIs (e.g. Seeking Alpha + TradingView).

So: **the “key” you add for Seeking Alpha is the RapidAPI key** (for the Seeking Alpha API on RapidAPI), not a key from seekingalpha.com.

---

## 3. Investing.com / Investing Pro — No official API

**Investing.com does not offer an official “InvestingPro API” or public API keys** for programmatic access.

Common approaches:

- **Unofficial libraries / scrapers:**  
  e.g. community projects that scrape or use non-public endpoints. These can break when the site changes and may conflict with Investing.com’s terms of service. Use at your own risk.
- **Third‑party data providers** that offer “Investing.com-like” or similar fundamental/technical data (e.g. EOD Historical Data, Polygon, Alpha Vantage). You’d use that provider’s API key instead of an “Investing Pro” key.
- **Manual / internal use:**  
  Use Investing Pro in the browser for research and enter or upload data into your own tools.

**In this app:** All four platforms are always active. For Investing Pro we use **yfinance** (free) for fundamentals (P/E, profitability, valuation) when **`INVESTING_PRO_API_KEY`** is unset. You can optionally set a third-party provider key later.

**Best option for this app:**  
Leave **`INVESTING_PRO_API_KEY`** unset to use built-in yfinance data, or set a key if you later integrate a paid provider (e.g. EOD, Polygon).

---

## 4. TradingView — No simple public API key from TradingView

**TradingView does not give a standard “TradingView API key”** for pulling stock data the way we do in this app. Their main product is the charting/analysis platform.

Ways to get “TradingView-like” or market data:

- **TradingView Data API (e.g. on RapidAPI):**  
  Some third-party “TradingView” or “TradingView Data” APIs exist on RapidAPI. You get a key from RapidAPI, not from tradingview.com. If we integrate one, we’d use something like **`TRADINGVIEW_API_KEY`** or **`RAPIDAPI_KEY`** for that API.
- **Other market data APIs:**  
  EOD Historical Data, Polygon, Alpha Vantage, Yahoo Finance, etc. These give OHLC, fundamentals, and sometimes ratings. We could use one of them and label it as “TradingView” in the UI if you want a single “TradingView” slot.
- **Scraping TradingView:**  
  Possible in theory but fragile and may violate ToS. Not recommended as the primary approach.

**In this app:** The TradingView slot is always active. We use **yfinance** (free) for technical data (price vs SMAs, momentum) when **`TRADINGVIEW_API_KEY`** is unset. You can optionally set a market data API key (e.g. EOD, Polygon, Alpha Vantage) in **`TRADINGVIEW_API_KEY`** for enhanced data later.

---

## Summary: What to actually set in Render

| Env variable            | Best way to get “key” | Notes |
|-------------------------|------------------------|-------|
| **DANELFIN_API_KEY**    | Subscribe at danelfin.com/pricing/api; use the key they send. | Official API; use `x-api-key` header. |
| **SEEKING_ALPHA_API_KEY** | RapidAPI key for the “Seeking Alpha” API on RapidAPI. | No direct key from seekingalpha.com. |
| **INVESTING_PRO_API_KEY** | No real API from Investing.com. | Leave unset or use another provider’s key and wire it in code. |
| **TRADINGVIEW_API_KEY**  | No key from tradingview.com. Use a market data API key (EOD, Polygon, etc.) and map it in code. | Or leave unset and use other sources. |

---

## If you don’t have any keys yet

The app is designed to work **without** these keys: it uses **demo/synthetic data** so you still get rankings and top 20 picks. When you add real keys (Danelfin, RapidAPI for Seeking Alpha, and optionally a market data API for “TradingView”), the backend can be updated to call the real APIs and the same env vars can be used.

Next step on our side: we can (1) implement the **Danelfin** client with `x-api-key` and their docs, (2) add **RapidAPI**-based calls for the **Seeking Alpha** API and document that `SEEKING_ALPHA_API_KEY` = RapidAPI key, and (3) optionally add one **market data provider** (e.g. EOD or Alpha Vantage) and use it for the “TradingView” slot. If you tell me which of these you want first (Danelfin, Seeking Alpha, or a market data API), I can outline the exact code changes next.
