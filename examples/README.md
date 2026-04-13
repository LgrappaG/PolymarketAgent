# Examples

This directory contains practical examples showing how to use PolymarketAgent.

## 📚 Example Files

### `basic_setup.py`
Getting started - configure the system and run a simple analysis.

### `custom_strategy.py`
Build your own trading strategy using Claude tools.

### `data_collection_example.py`
Use the data collectors independently for research.

### `paper_trading_example.py`
Run paper (simulated) trading without real money.

## Quick Start: Run Your First Example

```bash
# Set up environment (if not done)
cd PolymarketAgent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template (no edits needed for paper trading)
cp .env.example .env.local

# Run a demo example
python examples/basic_setup.py
```

## Example 1: Basic Setup

[See `basic_setup.py`]

This example shows:
- Loading configuration
- Initializing Claude agent
- Running data collectors
- Generating analysis

**Run it:**
```bash
python examples/basic_setup.py
```

## Example 2: Custom Trading Strategy

[See `custom_strategy.py`]

Learn how to:
- Define custom decision logic
- Use Claude tools for analysis
- Create trading signals
- Backtest strategies

**Run it:**
```bash
python examples/custom_strategy.py
```

## Example 3: Data Collection

[See `data_collection_example.py`]

Use individual collectors:
- Fetch polling data
- Get sports data
- Analyze news sentiment
- Collect crypto data

**Run it:**
```bash
python examples/data_collection_example.py
```

## Example 4: Paper Trading

[See `paper_trading_example.py`]

Simulate trading:
- Run in PAPER mode (no real money)
- Execute trades in simulation
- Track performance
- View results

**Run it:**
```bash
python examples/paper_trading_example.py
```

---

## Common Patterns

### Pattern 1: Use Claude for Analysis

```python
from src.agents.claude_agent import ClaudeAgent
from src.config import Settings

settings = Settings()
agent = ClaudeAgent(settings=settings)

# Analyze a market
result = agent.analyze_market(
    question="Will Bitcoin exceed $50k?",
    odds=0.38,
    related_data={"trend": "bullish", "news_sentiment": 0.6}
)

print(result)  # {'confidence': 0.82, 'decision': 'BUY', 'reasoning': '...'}
```

### Pattern 2: Collect Data

```python
from src.data.collectors import NewsCollector

collector = NewsCollector(api_key="your-newsapi-key")
articles = collector.fetch(query="Bitcoin", days=7)

for article in articles:
    print(f"{article['title']}: {article['sentiment']}")
```

### Pattern 3: Calculate Expected Value

```python
from src.agents.tools.ev_calculator import ev_calculator

# Market price: 0.38 (38% implied probability)
# Your estimate: 45%
ev = ev_calculator(
    market_odds=0.38,
    your_probability=0.45,
    confidence=0.85
)

print(f"Expected value: {ev['edge_percent']:.2f}%")
```

---

## Important Reminders

⚠️ **This is for LEARNING:**
- Examples use paper trading (simulated)
- Start in PAPER mode before doing real trades
- Never use production credentials for testing
- Keep test amounts small ($10-50)

---

## Next Steps

After running examples:
1. ✅ Read `README.md` for system overview
2. ✅ Explore `tests/` directory for more examples
3. ✅ Check `docs/` for architecture & design
4. ✅ Try modifying examples for your ideas
5. ✅ Consider contributing to the project!

---

For more details:
- `README.md` - Project overview & quick start
- `docs/ARCHITECTURE.md` - System design
- `CONTRIBUTING.md` - How to contribute
- `tests/README.md` - Test examples
