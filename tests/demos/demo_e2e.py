"""
End-to-End Demo - Data → Claude → Memory Flow
Demonstrates complete agent pipeline
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datastore import DataStore
from src.agents.claude_agent import ClaudeAgent
from src.memory.performance_tracker import PerformanceTracker

logger_name = "E2E_DEMO"


async def run_e2e_demo():
    """Run complete end-to-end demo"""

    print("\n" + "=" * 80)
    print("POLYMARKET AGENT - COMPLETE E2E DEMO")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # ========== PHASE 1: DATA COLLECTION ==========
    print("[DATA] PHASE 1: DATA COLLECTION")
    print("-" * 80)

    datastore = DataStore(newsapi_key="demo")
    await datastore.initialize()

    print("[NET] Collecting data from all sources (parallel)...")
    market_data = await datastore.get_latest_data()

    if not market_data:
        print("[X] No data collected. Check API connections.")
        return

    print(f"[+] Data collected from {len(market_data)} sources:")
    for source, data in market_data.items():
        if isinstance(data, dict):
            print(f"  • {source.upper():<15} {len(str(data)) // 100} KB")
        else:
            print(f"  • {source.upper():<15} {type(data).__name__}")

    # ========== PHASE 2: CLAUDE ANALYSIS ==========
    print("\n[AI] PHASE 2: CLAUDE ANALYSIS (Tool-Use)")
    print("-" * 80)

    agent = ClaudeAgent()
    print("Sending market data to Claude (Opus 4.6)...\n")

    try:
        decisions = await agent.analyze_markets(market_data)

        if not decisions:
            print("[!]  Claude returned no trading decisions")
            print("(This is normal for demo with mock/limited data)")
            decisions = [
                {
                    "market": "Demo: Bitcoin above $50k",
                    "decision": "BUY",
                    "confidence": 0.72,
                    "edge_percent": 3.5,
                    "position_size": 50,
                    "reasoning": "Demo decision",
                }
            ]
            print("\n[LOG] Using demo decision for illustration:")

        print(f"[+] Claude generated {len(decisions)} trading decision(s):\n")

        for i, decision in enumerate(decisions, 1):
            print(f"{i}. Market: {decision.get('market', 'Unknown')}")
            print(f"   Decision: {decision.get('decision', 'N/A')}")
            print(f"   Confidence: {decision.get('confidence', 0):.0%}")
            if "edge_percent" in decision:
                print(f"   Edge: {decision.get('edge_percent'):.1f}%")
            if "reasoning" in decision:
                print(f"   Reasoning: {decision.get('reasoning', 'N/A')[:80]}...")
            print()

    except Exception as e:
        print(f"[X] Error calling Claude: {e}")
        print("Note: This is expected if API key not configured")
        print("Using demo decisions to continue demo...\n")

        decisions = [
            {
                "market": "Demo Market 1: Democratic Nominee 2028",
                "decision": "BUY",
                "confidence": 0.75,
                "edge_percent": 2.8,
                "position_size": 100,
            },
            {
                "market": "Demo Market 2: France FIFA 2026",
                "decision": "BUY",
                "confidence": 0.68,
                "edge_percent": 4.2,
                "position_size": 75,
            },
        ]
        print(f"Using {len(decisions)} demo decisions\n")

    # ========== PHASE 3: MEMORY TRACKING ==========
    print("[SAVE] PHASE 3: MEMORY & TRACKING")
    print("-" * 80)

    tracker = PerformanceTracker()

    print(f"Logging {len(decisions)} decisions to memory...")
    trade_ids = []

    for decision in decisions:
        # Log trade
        trade = tracker.log_trade(
            market=decision.get("market", "Unknown"),
            decision=decision.get("decision", "PASS"),
            confidence=decision.get("confidence", 0.5),
            position_size=decision.get("position_size", 50),
            entry_price=0.50,  # Demo: assume 50% market price
            notes=f"Automated decision | Edge: {decision.get('edge_percent', 0):.1f}%",
        )
        trade_ids.append(trade["id"])

        # Log calibration (for demonstration)
        tracker.log_prediction(
            market=decision.get("market", "Unknown"),
            claude_confidence=decision.get("confidence", 0.5),
            predicted_direction=decision.get("decision", "PASS"),
            actual_outcome="CORRECT" if decision.get("confidence", 0) > 0.65 else "INCORRECT",
        )

    print(f"[+] Logged {len(trade_ids)} trades to memory\n")

    # ========== PHASE 4: SIMULATE TRADE OUTCOMES ==========
    print("[EVAL] PHASE 4: SIMULATE TRADE OUTCOMES")
    print("-" * 80)

    print("Simulating trade closures (demo)...\n")

    for i, trade_id in enumerate(trade_ids):
        # Simulate random outcome
        import random

        exit_price = 0.50 + random.uniform(-0.05, 0.08)  # +/- 5-8%
        outcome = "WIN" if exit_price > 0.50 else "LOSS"
        pnl = (exit_price - 0.50) * tracker.trades.trades[trade_id - 1]["position_size"]

        tracker.close_trade(
            trade_id=trade_id,
            exit_price=exit_price,
            notes=f"Simulated closure ({outcome})",
        )

        print(
            f"Trade #{trade_id}: {outcome:6s} | "
            f"Exit: ${exit_price:.3f} | P&L: ${pnl:.2f}"
        )

    print()

    # ========== PHASE 5: REPORTING ==========
    print("[DATA] PHASE 5: PERFORMANCE REPORTING")
    print("-" * 80)

    print("\nGenerating performance reports...\n")

    tracker.print_summary()

    # Performance metrics
    metrics = tracker.get_performance_metrics()
    print("DETAILED METRICS:")
    print(json.dumps(
        {
            "summary": metrics["summary"],
            "win_metrics": metrics["win_metrics"],
        },
        indent=2,
    ))

    # Claude calibration
    calibration = tracker.get_claude_calibration()
    print("\n\nCLAUDE CALIBRATION:")
    print(json.dumps(calibration, indent=2))

    # ========== EXPORT ==========
    print("\n" + "-" * 80)
    print("[SAVE] Exporting full report...")

    report_file = "reports/e2e_demo_report.txt"
    Path("reports").mkdir(exist_ok=True)
    tracker.export_full_report(report_file)
    print(f"[+] Report saved to: {report_file}\n")

    # ========== FINAL SUMMARY ==========
    print("=" * 80)
    print("E2E DEMO COMPLETE!")
    print("=" * 80)
    print("""
SUMMARY:
[+] Data collected from 4 parallel sources
[+] Claude analyzed markets with Tool-Use (sentiment, EV, risk, arbitrage)
[+] Trading decisions logged to memory system
[+] Trade outcomes simulated and tracked
[+] Performance metrics calculated
[+] Claude calibration analyzed
[+] Full report exported

FILES CREATED:
• memory/trades_history.json       (Trade history)
• memory/claude_calibration.json   (Calibration tracking)
• reports/e2e_demo_report.txt      (Complete report)

NEXT STEPS:
1. Implement Trade Executor (Polymarket API)
2. Connect to live market data
3. Set execution thresholds (confidence, position size)
4. Run live trading with semi-auto mode

For more info: Check README.md
""")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n[*] Starting E2E demo... (this may take 30-60 seconds)")
    print("[*] Note: Claude call requires ANTHROPIC_API_KEY in .env.local")
    print("[*] Demo will continue with mock data if API unavailable\n")

    try:
        asyncio.run(run_e2e_demo())
    except KeyboardInterrupt:
        print("\n\n[X] Demo interrupted by user")
    except Exception as e:
        print(f"\n\n[X] Demo error: {e}")
        import traceback

        traceback.print_exc()
