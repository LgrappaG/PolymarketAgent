# System Architecture

## Overview

PolymarketAgent is a **4-layer autonomous trading system** that combines multi-source data analysis with Claude AI decision-making.

```
┌────────────────────────────────────────────────────────────┐
│                    INPUT: USER QUESTION                    │
│           "Will Biden lead Democratic ticket 2028?"        │
└────────────────────────┬─────────────────────────────────┘
                         │
      ┌──────────────────▼──────────────────┐
      │      LAYER 1: DATA COLLECTION       │
      │  (Parallel collectors with cache)   │
      └──────────────────┬──────────────────┘
                         │
      ┌─────────────────────────────────────────────────────┐
      │  • Polls (FiveThirtyEight real-time): 45% Biden    │
      │  • News Analytics (NewsAPI + sentiment): +0.8 score│
      │  • Social Media (Twitter): 78% positive sentiment   │
      │  • Historical Data: 2020 election patterns          │
      └──────────────────┬──────────────────────────────────┘
                         │
      ┌──────────────────▼──────────────────┐
      │   LAYER 2: CLAUDE DECISION ENGINE   │
      │        (Tool-Use Framework)         │
      └──────────────────┬──────────────────┘
                         │
      ┌─────────────────────────────────────────────────────┐
      │  Claude receives:                                   │
      │  - Market Question & Current Odds (35%)             │
      │  - Data from all collectors                         │
      │  - Historical context                               │
      │                                                      │
      │  Claude runs tools in sequence:                      │
      │  1. sentiment_analyzer()    → +2.8% net sentiment   │
      │  2. ev_calculator()         → 42% fair value        │
      │  3. risk_calculator()       → Kelly: 3% position    │
      │  4. arbitrage_detector()    → No arbs found         │
      │  5. confidence_scorer()     → 82% confidence        │
      │                                                      │
      │  Claude decides: "BUY $100 at 0.35"                │
      └──────────────────┬──────────────────────────────────┘
                         │
      ┌──────────────────▼──────────────────┐
      │  LAYER 3: EXECUTION & RISK         │
      │    (Semi-Autonomous Decision)       │
      └──────────────────┬──────────────────┘
                         │
      ┌─────────────────────────────────────────────────────┐
      │  IF confidence > 75% AND size < $50:                │
      │     → AUTO-EXECUTE (immediate)                      │
      │  ELIF 60% < confidence < 75%:                       │
      │     → QUEUE FOR APPROVAL (human reviews)            │
      │  ELSE:                                               │
      │     → REJECT (low confidence)                       │
      │                                                      │
      │  Risk checks (always):                              │
      │     • Position size < 2% of balance                │
      │     • Loss limit < 5% of balance                    │
      │     • Confidence threshold > 60%                    │
      └──────────────────┬──────────────────────────────────┘
                         │
      ┌──────────────────▼──────────────────┐
      │   LAYER 4: MEMORY & TRACKING        │
      │      (Performance Analysis)          │
      └──────────────────┬──────────────────┘
                         │
      ┌─────────────────────────────────────────────────────┐
      │  • trades_history.json: All exec'd trades + PnL    │
      │  • claude_calibration.json: Confidence vs. accuracy │
      │  • performance_metrics.json: Win rate, ROI, Sharpe │
      │  • category_analysis.json: Performance by market   │
      └─────────────────────────────────────────────────────┘
                         │
                         ▼
          ┌─────────────────────────────┐
          │  OUTPUT: Trade Execution    │
          │  + Performance Tracking      │
          └─────────────────────────────┘
```

---

## Layer Details

### Layer 1: Data Collection

**Purpose:** Gather multi-source data about markets in parallel.

**Components:**
```
DataStore (cache manager)
├── PolsCollector (FiveThirtyEight)
│   └── Polling data for politics markets
├── NewsCollector (NewsAPI)
│   └── News sentiment analysis
├── SportsCollector (ESPN)
│   └── Historical & real-time sports data
└── CryptoCollector (Binance, Whale Alert)
    └── Price & trading volume data
```

**Data Flow:**
1. Request data for a market
2. Check cache (TTL-based invalidation)
3. Fetch fresh data from APIs if needed
4. Return normalized data structure

**Example Output:**
```json
{
  "polls": [{"date": "2026-04-13", "biden": 45, "trump": 48}],
  "news_sentiment": {"positive": 0.62, "neutral": 0.25, "negative": 0.13},
  "crypto_price": {"btc": 52000, "eth": 2800},
  "recent_volume": 1250000
}
```

### Layer 2: Claude Decision Engine

**Purpose:** AI-powered decision making using Claude's tool-use capability.

**Tool Chain:** Claude processes data through specialized tools in sequence:

#### Tool 1: `sentiment_analyzer()`
```python
# Extracts sentiment from news/social media
Input: [news articles, tweets, data points]
Output: {
  "overall_sentiment": 0.62,  # -1.0 (bear) to +1.0 (bull)
  "confidence": 0.78,
  "top_signals": ["Biden polling up", "Market reacts positively"],
  "edge": "+2.8%"  # vs. current market odds
}
```

#### Tool 2: `ev_calculator()`
```python
# Calculate expected value vs. market odds
Input: {
  "market_odds": 0.35,  # What market is pricing
  "model_probability": 0.42,  # What we think
  "confidence": 0.85
}
Output: {
  "fair_value": 0.42,
  "edge_percent": "+6.0%",  # 42% vs. 35% market
  "decision": "BUY",
  "rationale": "Underpriced by 6%"
}
```

#### Tool 3: `risk_calculator()`
```python
# Kelly Criterion for position sizing
Input: {
  "confidence": 0.82,
  "avg_historical_win": 1.5,
  "avg_historical_loss": 1.0,
  "account_balance": 500
}
Output: {
  "kelly_fraction": 0.03,  # 3% of balance
  "recommended_size": 15,  # $15 trade
  "max_loss": 0.75  # -$0.75 max downside
}
```

#### Tool 4: `arbitrage_detector()`
```python
# Spot cross-market inefficiencies
Input: {
  "market_id": "biden_2028",
  "polymarket_odds": 0.35,
  "pinnacle_odds": 0.34,  # Bookmaker
  "betfair_odds": 0.36
}
Output: {
  "arbitrage_found": false,
  "best_spread": "Polymarket vs. Betfair: 1%",
  "recommendation": "No arb opportunity"
}
```

**Claude's Decision Process:**
1. Receives all data from Layer 1
2. Calls tools in intelligent sequence
3. Analyzes results holistically
4. Generates trade recommendation with confidence
5. Returns structured decision JSON

### Layer 3: Execution & Risk Management

**Purpose:** Execute trades with human oversight & risk controls.

**Execution Modes:**
```
┌─ PAPER (Simulation)
│  └─ No real transactions, test strategies
│
├─ APPROVAL (Human Review)
│  └─ Trades queued for human approval before execution
│  └─ 60-75% confidence trades wait here
│
└─ AUTO (Fully Automatic)
   └─ High-confidence (>75%) trades auto-execute
   └─ Small trades (<$50) only
```

**Risk Checks (Always Applied):**
```python
# Position Sizing
if position_size > (balance * 0.02):
    reject("Position exceeds 2% limit")

# Confidence Threshold
if confidence < 0.60:
    reject("Confidence too low")

# Cumulative Loss Prevention
if daily_loss > (balance * 0.05):
    reject("Daily loss limit exceeded")

# Odd Sanity Checks
if odds < 0.01 or odds > 0.99:
    reject("Odds outside valid range")
```

**Execution Flow:**
```
Decision from Claude
        │
        ▼
   Risk Checks
        │
    ┌───┴────┬────────┬──────────┐
    │        │        │          │
   REJECT  APPROVAL  AUTO     QUEUE
    │        │        │          │
Discard  Human Wait Execute    Wait
        Review
```

### Layer 4: Memory & Tracking

**Purpose:** Log trades, track performance, enable learning.

**Memory Structures:**

#### `trades_history.json`
```json
{
  "trades": [
    {
      "id": 1,
      "timestamp": "2026-04-13T16:12:54",
      "market": "Will Biden lead Democratic ticket?",
      "decision": "BUY",
      "confidence": 0.82,
      "entry_price": 0.35,
      "position_size": 100,
      "exit_price": 0.38,
      "pnl": 3.00,
      "pnl_percent": 2.86,
      "status": "CLOSED",
      "closed_at": "2026-04-13T17:30:00"
    }
  ]
}
```

#### `claude_calibration.json`
```json
{
  "calibration": [
    {
      "confidence_bin": "0.8-0.9",
      "avg_confidence": 0.85,
      "accuracy": 0.78,  // What % of high-confidence trades won?
      "sample_size": 42
    },
    {
      "confidence_bin": "0.6-0.7",
      "avg_confidence": 0.65,
      "accuracy": 0.55,
      "sample_size": 18
    }
  ]
}
```

#### `performance_metrics.json`
```json
{
  "summary": {
    "total_trades": 60,
    "winning_trades": 42,
    "losing_trades": 18,
    "win_rate": 0.70,
    "gross_profit": 145.32,
    "gross_loss": -42.18,
    "net_profit": 103.14,
    "roi_percent": 20.6,
    "sharpe_ratio": 1.82
  },
  "by_category": {
    "politics": {"win_rate": 0.75, "roi": 25.3},
    "sports": {"win_rate": 0.62, "roi": 15.2},
    "crypto": {"win_rate": 0.48, "roi": -5.1}
  }
}
```

---

## Data Flow Example

**Scenario:** User asks "Will Bitcoin exceed $50k by end of Q2 2026?"

```
Step 1: User Input
└─ Question: "Bitcoin $50k by June 30?"
  Polymarket Price: 0.42 (42% implied)

Step 2: Data Collection (Layer 1)
├─ CryptoCollector: BTC=$49,200 (+3% this week)
├─ NewsCollector: 45 articles (sentiment: +0.65)
├─ SocialMedia: Twitter trending (positive mentions: 3.2x)
└─ TechnicalData: RSI=62, MA trending up

Step 3: Claude Analysis (Layer 2)
├─ Tool: sentiment_analyzer()
│  └─ Result: "Strong bullish sentiment, +3.2% vs. market"
├─ Tool: ev_calculator()
│  └─ Result: "Fair value ~48%, market at 42%, +6% edge"
├─ Tool: risk_calculator()
│  └─ Result: "Kelly position: $32 (3% of balance)"
└─ Claude Decision: BUY at 0.42, 85% confidence

Step 4: Execution (Layer 3)
├─ Position size $32 < $50 limit ✓
├─ Confidence 85% > 75% threshold ✓
└─ Execute immediately (AUTO mode)

Step 5: Tracking (Layer 4)
├─ Log: {market, price, size, time, confidence}
├─ Track: Entry price vs. exit price → P&L
└─ Calibrate: Did 85% confidence prediction work?
```

---

## Key Features

### Caching Strategy

```python
# Data cached with TTL
polls_data: 6 hours (slow to update)
news_sentiment: 1 hour (changes frequently)
crypto_prices: 5 minutes (very volatile)
```

### Error Handling

```python
# Graceful fallback for API failures
if api_fails:
    use_cached_data()
if all_data_fails:
    skip_market()     # Don't trade without data
    log_alert()       # Notify operator
```

### Async Data Collection

```python
# Fetch data in parallel
tasks = [
    fetch_polls(),
    fetch_news(),
    fetch_crypto(),
    fetch_sports()
]
results = await asyncio.gather(*tasks)
```

---

## Performance Optimization

### Caching
- DataStore holds 100+ cached results
- TTL = invalidation time per data type
- Falls back to cache on API timeout

### Rate Limiting
- NewsAPI: 3 req/min (free tier)
- Polymarket: Optimized for batch queries
- Twitter: 450 req/15min (depends on tier)

### Batching
- Process 50+ markets in parallel
- Single API call for data collection
- Parallel Claude tool invocations

---

## Configuration

Edit `.env.local` to customize:

```env
EXECUTION_MODE=PAPER          # PAPER | APPROVAL | AUTO
MAX_POSITION_SIZE=0.02        # 2% per trade
MIN_CONFIDENCE_AUTO=0.75      # Auto-execute threshold
MIN_CONFIDENCE_APPROVAL=0.60  # Requires human review
```

---

## Future Enhancements

- [ ] Real-time Polymarket order book integration
- [ ] Multi-market hedging strategies
- [ ] Sentiment analysis using local LLM
- [ ] Advanced portfolio optimization
- [ ] Backtesting framework

---

## Security Considerations

- Private keys stored in `.env.local` (gitignored)
- API keys never logged or exposed
- Trades only execute in configured mode
- Risk checks always active, cannot be disabled
- Memory sanitized of sensitive data

---

For more details, see:
- `README.md` - Quick start & overview
- `CONTRIBUTING.md` - How to extend the system
- `tests/demos/` - Working examples
