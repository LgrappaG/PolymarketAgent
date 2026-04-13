"""
Test direct tool-use without full pipeline
Debug: Check if tools are working
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.tools.sentiment_analyzer import sentiment_analyzer
from src.agents.tools.ev_calculator import expected_value_calculator
from src.agents.tools.risk_calculator import risk_calculator
from src.agents.tools.arbitrage_detector import arbitrage_detector


async def test_tools():
    """Test each tool directly"""

    print("\n" + "=" * 70)
    print("DIRECT TOOL-USE TEST")
    print("=" * 70 + "\n")

    # Test 1: Sentiment Analyzer
    print("[1] Sentiment Analyzer")
    print("-" * 70)
    result1 = sentiment_analyzer(
        market="Democratic Nominee 2028",
        text="Biden leads in latest polls, strong approval ratings this quarter"
    )
    print(f"Result: {result1}\n")

    # Test 2: EV Calculator
    print("[2] Expected Value Calculator")
    print("-" * 70)
    result2 = expected_value_calculator(
        market_price=0.35,
        model_probability=0.42,
        kelly_fraction=0.5
    )
    print(f"Result: {result2}\n")

    # Test 3: Risk Calculator
    print("[3] Risk Calculator")
    print("-" * 70)
    result3 = risk_calculator(
        balance=1000,
        confidence=0.75,
        edge=0.07,
        market_price=0.35
    )
    print(f"Result: {result3}\n")

    # Test 4: Arbitrage Detector
    print("[4] Arbitrage Detector")
    print("-" * 70)
    result4 = arbitrage_detector(
        polymarket_price=0.50,
        competitor_price=0.52,
        competitor_name="DraftKings"
    )
    print(f"Result: {result4}\n")

    # Synthesis
    print("[SYNTHESIS] Decision Logic")
    print("-" * 70)

    decisions = []

    # Decision 1: If EV positive (decision=BUY) + sentiment positive
    ev_bullish = result2.get("decision") == "BUY"
    sentiment_bullish = result1.get("sentiment", 0) > 0.7

    if ev_bullish and sentiment_bullish:
        print(f"[+] EV BUY signal + sentiment bullish -> BUY decision")
        print(f"    EV edge: {result2.get('edge_percent'):.1f}% | Confidence: {result2.get('confidence'):.0%}")
        decisions.append({
            "market": "Democratic Nominee 2028",
            "decision": "BUY",
            "confidence": min(result2.get("confidence", 0.5), 0.85),
        })

    # Decision 2: Arbitrage opportunity
    if result4.get("arbitrage_exists"):
        print(f"[+] Arbitrage opportunity detected -> BUY signal")
        print(f"    Margin: {result4.get('margin_percent', 0):.2f}% | Confidence: {result4.get('confidence'):.0%}")
        decisions.append({
            "market": "Arbitrage: Polymarket vs Competitor",
            "decision": "BUY",
            "confidence": result4.get("confidence", 0.5),
        })

    # Filter by min confidence 0.70
    min_conf = 0.70
    final = [d for d in decisions if d.get("confidence", 0) >= min_conf]

    print(f"\nTotal signals: {len(decisions)}")
    print(f"After min_confidence={min_conf:.0%} filter: {len(final)}")

    if final:
        print("\n[FINAL DECISIONS]:")
        for d in final:
            print(f"  - {d['market']:<35} {d['decision']:>4} @ {d['confidence']:.0%}")
    else:
        print("\n[!] No decisions pass confidence threshold (too conservative)")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_tools())
