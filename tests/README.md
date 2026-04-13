# Tests & Demos

This directory contains tests, demos, and debug scripts organized by category.

## Quick Start

### Run All Unit Tests (No Credentials Required)

```bash
pytest tests/unit/ -v
```

### Run Demos (Educational - Shows How System Works)

```bash
cd tests/demos
python demo.py
python demo_e2e.py
```

## Directory Structure

### 📚 `demos/` - Educational Demos

Standalone scripts showing how the system works. **No credentials required.**

- `demo.py` - Basic system initialization and data collection
- `demo_e2e.py` - End-to-end flow: data → decision → execution
- `demo_e2e_full.py` - Complete flow with all components
- `demo_mock_live_trade.py` - Simulated live trading example

**Run these to learn:**
```bash
python tests/demos/demo.py
python tests/demos/demo_e2e.py
```

---

### 🧪 `unit/` - Unit Tests

Traditional unit tests using pytest. **No credentials or external APIs required.**

- `test_agents.py` - Claude agent & tool-use tests
- `test_tools_direct.py` - Individual tool tests (sentiment, EV calc, etc.)

**Run all unit tests:**
```bash
pytest tests/unit/ -v
pytest tests/unit/ --cov=src  # With coverage report
```

**Run specific test:**
```bash
pytest tests/unit/test_agents.py::test_agent_initialization -v
```

---

### 🔗 `integration/` - Integration Tests

Tests that interact with real APIs. **Requires `.env.local` with REAL credentials.**

⚠️ **WARNING:** Only run if you have:
- Valid Polymarket API credentials
- Test/demo wallet (NOT production)
- Small test balance (NOT real money)

- `test_auth.py` - Authentication with Polymarket
- `test_live_order_status.py` - Query live order status
- `test_direct_order.py` - Direct order placement (paper/approval mode)
- `check_account_balance.py` - Check wallet balance
- `test_live_execution.py` - Full execution pipeline

**Run integration tests:**
```bash
# Ensure .env.local is configured with TEST credentials
pytest tests/integration/ -v
```

**Important:** These tests interact with real Polymarket testnet. Keep balances small.

---

### 🐛 `debug/` - Debug & Inspection Scripts

Troubleshooting and inspection tools. Use these to diagnose issues.

- `debug_live_execution.py` - Debug execution pipeline
- `debug_signature.py` - Verify blockchain signatures
- `inspect_market_structure.py` - Examine market data structure
- `preflight_check.py` - System health check

**Run diagnostics:**
```bash
python tests/debug/preflight_check.py     # Check if system is ready
python tests/debug/inspect_market_structure.py  # Examine markets
```

---

### 📊 `report_generators/` - Reporting & Analysis

Scripts for generating performance reports and session analysis.

- `export_stats.py` - Export trading statistics
- `trading_session.py` - Run trading session
- `micro_trading_session.py` - Small test trading session
- `paper_trading_full.py` - Full paper trading test
- `live_trading.py` - Live trading session runner
- `multi_session_analysis.py` - Compare multiple trading sessions

**Generate reports:**
```bash
python tests/report_generators/export_stats.py
python tests/report_generators/multi_session_analysis.py
```

---

## Running All Tests

### Full Test Suite

```bash
# Unit tests only (fast, no external deps)
pytest tests/unit/ -v

# Unit + Integration (requires credentials)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black tests/ src/

# Lint
flake8 tests/ src/

# Type checking
mypy tests/ src/
```

---

## Test Coverage

Current coverage target: **70%+**

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing
```

---

## Important Notes

### ⚠️ This is a TEST System

- All tests are for **learning & validation only**
- Integration tests use **test/demo credentials**
- Demo trades are **paper (simulated) only**
- **NEVER** use real credentials or production accounts

### Best Practices

✅ **Do:**
- Start with demos to understand system
- Run unit tests frequently
- Use integration tests only with test accounts
- Check logs when debugging

❌ **Don't:**
- Run integration tests against production
- Use real money for testing
- Commit `.env.local` to git
- Share credentials in issues/code

---

## Troubleshooting

### Tests Won't Run

```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt

# Try running single test
pytest tests/unit/test_agents.py -v
```

### Integration Tests Fail

```bash
# Verify credentials
python tests/debug/preflight_check.py

# Check market data
python tests/debug/inspect_market_structure.py

# Examine logs
cat logs/latest.log
```

### Import Errors

```bash
# Ensure you're in project root
cd PolymarketAgent

# Activate venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run test
pytest tests/unit/ -v
```

---

## Contributing Tests

See `CONTRIBUTING.md` for guidelines on adding tests.

---

For more information:
- `README.md` - Project overview
- `docs/ARCHITECTURE.md` - System design (coming soon)
- `CONTRIBUTING.md` - Contribution guidelines
