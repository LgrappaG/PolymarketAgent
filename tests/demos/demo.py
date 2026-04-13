"""
Demo Script - Test Claude Agent with Sample Data
Run: python tests/demo.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.claude_agent import ClaudeAgent


async def run_demo():
    """Run demo analysis with sample market data"""

    print("\n" + "=" * 70)
    print("POLYMARKET AGENT - CLAUDE TOOL-USE DEMO")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    # Initialize agent
    agent = ClaudeAgent()

    # === DEMO 1: Politics Market ===
    print("🧠 DEMO 1: Politics Market Analysis")
    print("-" * 70)

    politics_data = {
        "type": "politics",
        "market_name": "Will Democrat nominee be different from Biden in 2028?",
        "polymarket_price": 0.38,
        "market_id": "dem-2028-nominee",
        "latest_news": [
            "FiveThirtyEight: Biden support at 41% (up from 38% last week)",
            "New York Times: Democratic insiders express concern about November",
            "Twitter: #DemocraticParty trending - mostly supportive posts",
        ],
        "polling_trend": "+3% in last 7 days",
        "competitor_odds": "Pinnacle: 2.40 (implies 42%)",
    }

    print(f"Market: {politics_data['market_name']}")
    print(f"Polymarket Price: {politics_data['polymarket_price']:.0%}")
    print(f"Recent Trend: {politics_data['polling_trend']}")
    print()

    politics_decisions = await agent.analyze_markets(
        {"politics": politics_data}
    )

    print("Claude Decisions:")
    for decision in politics_decisions:
        print(json.dumps(decision, indent=2))

    # === DEMO 2: Sports Market ===
    print("\n🧠 DEMO 2: Sports Market Analysis")
    print("-" * 70)

    sports_data = {
        "type": "sports",
        "market_name": "France wins FIFA 2026",
        "polymarket_price": 0.18,
        "market_id": "fifa-2026-france",
        "recent_form": "France beat Bulgaria 4-0 (Euro qualifier)",
        "key_players": "Mbappé fit, Griezmann in form",
        "news": [
            "France advances to World Cup finals",
            "Benzema retirement impact minimal",
            "Tactical innovation praised by analysts",
        ],
        "competitor_odds": {"Pinnacle": 4.50, "Betfair": 4.40},
    }

    print(f"Market: {sports_data['market_name']}")
    print(f"Polymarket Price: {sports_data['polymarket_price']:.0%}")
    print(f"Recent Form: {sports_data['recent_form']}")
    print(f"Competitor Odds: {sports_data['competitor_odds']}")
    print()

    sports_decisions = await agent.analyze_markets({"sports": sports_data})

    print("Claude Decisions:")
    for decision in sports_decisions:
        print(json.dumps(decision, indent=2))

    # === DEMO 3: Crypto Arbitrage ===
    print("\n🧠 DEMO 3: Crypto Arbitrage Market Analysis")
    print("-" * 70)

    crypto_data = {
        "type": "crypto",
        "market_name": "Bitcoin above $50k by April 2026",
        "polymarket_price": 0.42,
        "market_id": "btc-50k",
        "current_price": 48200,
        "binance_futures_signal": 0.45,
        "whale_activity": "Large inflows to major wallets",
        "fed_calendar": "Interest rate decision in 2 weeks",
        "news": [
            "Bitcoin ETF inflows continue",
            "Macroeconomic uncertainty remains",
            "Technical analysis: Cup and handle pattern",
        ],
    }

    print(f"Market: {crypto_data['market_name']}")
    print(f"Current BTC Price: ${crypto_data['current_price']}")
    print(f"Polymarket Price: {crypto_data['polymarket_price']:.0%}")
    print(f"Binance Signal: {crypto_data['binance_futures_signal']:.0%}")
    print()

    crypto_decisions = await agent.analyze_markets({"crypto": crypto_data})

    print("Claude Decisions:")
    for decision in crypto_decisions:
        print(json.dumps(decision, indent=2))

    # === Summary ===
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_decisions = politics_decisions + sports_decisions + crypto_decisions
    buy_count = sum(1 for d in all_decisions if d.get("decision") == "BUY")
    sell_count = sum(1 for d in all_decisions if d.get("decision") == "SELL")
    pass_count = sum(1 for d in all_decisions if d.get("decision") == "PASS")

    print(f"Total Opportunities Analyzed: {len(all_decisions)}")
    print(f"BUY Signals: {buy_count}")
    print(f"SELL Signals: {sell_count}")
    print(f"PASS (No edge): {pass_count}")
    print()

    if all_decisions:
        avg_confidence = sum(d.get("confidence", 0) for d in all_decisions) / len(
            all_decisions
        )
        print(f"Average Confidence: {avg_confidence:.0%}")

    print("=" * 70)
    print("✓ Demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print("\n⏳ Starting demo... (Claude API call in progress)")
    print("Note: First run may be slow (API latency)")
    asyncio.run(run_demo())
