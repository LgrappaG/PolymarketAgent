# 🧠 Polymarket AI Agent

> ⚠️ **DISCLAIMER: This is a TEST/DEMO PROJECT**
> 
> This is **research and educational software** demonstrating autonomous AI trading concepts.
> **NOT suitable for production use or real financial trading.**
> Use for learning and testing only. No warranty provided.

An autonomous trading agent for **Polymarket** prediction markets, powered by Claude AI and multi-source data analysis.

**Status:** 🚀 MVP Phase (Foundation & Configuration) - Educational/Test Purpose

---

## 📋 Features

### Current Phase (MVP)
- ✅ Project structure & configuration management
- ✅ Claude Tool-Use integration (decision engine)
- 🔄 Multi-source data collection (Polls, Sports, Crypto, News)
- 🔄 Semi-autonomous execution with confidence thresholds
- 🔄 Memory system for trade history & performance tracking

### Roadmap
- Phase 2: Full data collectors for all market categories
- Phase 3: Real-time Polymarket API integration
- Phase 4: Advanced risk management (Kelly Criterion)
- Phase 5: Backtesting framework

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  DATA LAYER (Collectors)                    │
├─────────────────────────────────────────────┤
│ • Polls (FiveThirtyEight)                   │
│ • Sports (ESPN)                             │
│ • Crypto (Binance, Whale Alert)             │
│ • News (NewsAPI, Twitter/X)                 │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  CLAUDE DECISION ENGINE (Tool-Use)          │
├──────────────────────────────────────────────┤
│ • Sentiment Analysis                        │
│ • Expected Value Calculation                │
│ • Risk Management                           │
│ • Arbitrage Detection                       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  EXECUTION (Semi-Autonomous)                │
├──────────────────────────────────────────────┤
│ IF confidence > 75% + size < $50:           │
│   → AUTO-EXECUTE                            │
│ IF 60-75% confidence:                       │
│   → QUEUE FOR APPROVAL                      │
│ ELSE:                                        │
│   → HUMAN REVIEW                            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  MEMORY (Tracking & Performance)            │
├──────────────────────────────────────────────┤
│ • Trade History                             │
│ • Win Rate by Category                      │
│ • Claude Calibration                        │
│ • Risk Metrics                              │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd PolymarketAgent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
cp .env.example .env.local
# Edit .env.local with your API keys:
# - ANTHROPIC_API_KEY (Claude)
# - POLYMARKET credentials
# - WALLET address & PRIVATE_KEY
# - Data source APIs (NewsAPI, Twitter, etc.)
```

### 3. Run Agent

```bash
python -m src.main
```

---

## 🔑 API Keys Required

### Must-Have
- **Anthropic Claude**: https://console.anthropic.com (free tier available)
- **Polymarket CLOB**: https://clob.polymarket.com (free, only gas)
- **News API**: https://newsapi.org (free: 100 req/day)

### Recommended
- **Twitter/X API v2**: $100/month (Essential tier) for tweet analysis
- **FiveThirtyEight**: Free polls (read-only)
- **ESPN API**: Free sports data

### Optional (Arbitrage)
- **Pinnacle**: Bookmaker odds API ($200-500/month)

---

## 📊 Market Categories & Strategies

| Category | Strategy | Target ROI | Risk |
|----------|----------|-----------|------|
| **Politics** | Polling + sentiment | +3-5% / week | 🟢 Low |
| **Sports** | Historical + injuries | +5-10% / week | 🟡 Medium |
| **Crypto** | Arbitrage + news | +2-4% / week | 🔴 High |
| **Arbitrage** | Cross-market spreads | +1-2% / week | 🟢 Low |

---

## 🧠 Decision Engine (Claude Tool-Use)

The agent uses Claude's tool-use capability to:

1. **Sentiment Analysis** - Extract market signals from news/tweets
2. **Expected Value Calc** - Compare market odds vs. model probability
3. **Risk Calculator** - Determine position size (Kelly Criterion)
4. **Arbitrage Detection** - Spot cross-market inefficiencies

Example decision flow:
```
Market: "Will Bitcoin exceed $50k by April 2026?"
Current odds: 0.38 (38% probability)
Claude thinks: 42% probability (based on data)
Edge: +4.2%
Confidence: 82%
Decision: BUY 0.38 odds (underpriced)
Position Size: $100 (1% of balance)
```

---

## 📝 Configuration

Key settings in `.env.local`:

```env
# Risk Parameters
INITIAL_BALANCE=500                 # Starting USDC
MAX_POSITION_SIZE=0.02             # 2% per trade
MIN_CONFIDENCE_AUTO=0.75           # Auto-execute threshold
MIN_CONFIDENCE_APPROVAL=0.60       # Needs human review

# Execution Mode
EXECUTION_MODE=APPROVAL  # PAPER | APPROVAL | AUTO
```

See `.env.example` for all options.

---

## 📂 Project Structure

```
polymarket-agent/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration & constants
│   ├── data/
│   │   ├── collectors/      # Market data sources
│   │   └── datastore.py     # Data caching
│   ├── agents/
│   │   ├── claude_agent.py  # Decision engine (Tool-Use)
│   │   └── tools/           # Claude tools
│   ├── execution/
│   │   ├── executor.py      # Trade executor
│   │   ├── polymarket_client.py
│   │   └── approval_queue.py
│   └── memory/
│       ├── trades_history.py
│       └── performance_tracker.py
├── tests/
├── logs/
├── .env.local              # Your secrets (GITIGNORE)
├── .env.example            # Template
└── requirements.txt
```

---

## 🔒 Security Notes

⚠️ **CRITICAL SECURITY & DISCLAIMER:**
- **This is NOT production software.** This is a proof-of-concept for educational purposes only.
- **Real financial risk:** Do not use with real money, real private keys, or production accounts.
- **For production deployment,** you would need:
  - Hardware security module (HSM) for key management
  - Professional security audit
  - Compliance review (securities regulation)
  - Institutional-grade monitoring & alerting
  - Insurance & liability coverage
- Never commit `.env.local` (private key stored here!)
- Use `.env.example` as template only
- Test in `PAPER` mode first (simulated trades)

💡 **Best Practices (For Learning):**
- Start in `PAPER` mode (simulation only)
- Graduate to `APPROVAL` (human review of each trade)
- Only then move to `AUTO` (fully automatic)
- Never use real credentials or significant amounts while learning

---

## 📊 Performance Tracking

Agent logs all trades to `memory/`:
- `trades_history.json` - All trades with PnL
- `category_performance.json` - Win rate by market type
- `claude_calibration.json` - Confidence accuracy metrics

```bash
# View performance
python -c "from src.memory import PerformanceTracker; \
           p = PerformanceTracker(); p.print_summary()"
```

---

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src  # Coverage report
```

---

## 🤝 Contributing

Current contributors: 1
Focus area: Core agent loop & Claude integration

---

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.

**All use is strictly for educational and testing purposes only.**

---

## 🎯 Next Steps

1. ✅ **Phase 1 (NOW):** Configure & validate API connections
2. 🔄 **Phase 2:** Build data collectors
3. 🔄 **Phase 3:** Claude decision engine
4. 🔄 **Phase 4:** Trade execution
5. 🔄 **Phase 5:** Memory & performance tracking

**Let's get this agent trading! 🚀**
