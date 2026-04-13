"""
Trading Session: 10 rounds with real Claude decisions
Paper mode (no real money) + Tool-use analysis + Performance tracking
"""

import asyncio
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datastore import DataStore
from src.agents.claude_agent import ClaudeAgent
from src.execution.executor import TradeExecutor
from src.execution.polymarket_connector import PolymarketConnector
from src.execution.risk_manager import RiskManager, RiskConfig
from src.memory.performance_tracker import PerformanceTracker
from src.config import get_settings


async def run_trading_session():
    """Run 10-round trading session"""

    print("\n" + "=" * 100)
    print("TRADING SESSION: 10 ROUNDS")
    print("=" * 100)
    print(f"Start Time: {datetime.now().isoformat()}\n")

    settings = get_settings()

    # Initialize
    datastore = DataStore(newsapi_key=settings.news_api_key)
    await datastore.initialize()

    agent = ClaudeAgent()
    connector = PolymarketConnector("test", "test", "test")
    await connector.initialize()

    risk_config = RiskConfig(initial_balance=10000)
    tracker = PerformanceTracker()
    executor = TradeExecutor(connector, risk_config, tracker)

    # Trading session
    total_pnl = 0
    total_trades = 0
    wins = 0

    for round_num in range(1, 11):
        print(f"[ROUND {round_num}/10]")
        print("-" * 100)

        # Fetch data
        market_data = await datastore.get_latest_data()

        # Get decisions
        decisions = await agent.analyze_markets(market_data)

        if decisions:
            print(f"  Decisions: {len(decisions)}")

            # Execute
            report = await executor.execute_decisions(
                decisions=decisions,
                market_data=market_data,
                execution_mode="PAPER"
            )

            executed = report['executed']
            total_trades += executed

            if executed > 0:
                print(f"  Executed: {executed} orders")

                # Simulate outcome
                for exec_order in report['executions']:
                    # Random outcome: 60% win rate
                    win = random.random() < 0.60
                    exit_price = exec_order['entry_price'] * (1 + random.uniform(-0.02, 0.05))
                    pnl = (exit_price - exec_order['entry_price']) * exec_order['position_size']

                    total_pnl += pnl
                    if pnl > 0:
                        wins += 1

                    status = "[WIN]" if pnl > 0 else "[LOSS]"
                    print(f"    {status} ${pnl:+.2f} | {exec_order['market'][:30]}")

        print(f"  Session P&L: ${total_pnl:+.2f}")
        print()

        await asyncio.sleep(0.5)  # Rate limit

    # Final report
    print("\n" + "=" * 100)
    print("TRADING SESSION COMPLETE")
    print("=" * 100)

    tracker.print_summary()

    print(f"\nSESSION STATS:")
    print(f"  Rounds: 10")
    print(f"  Total Orders: {total_trades}")
    print(f"  Total P&L: ${total_pnl:+.2f}")
    print(f"  Win Rate: {wins}/{total_trades} ({wins/max(1,total_trades)*100:.1f}%)")
    print(f"  ROI: {total_pnl/10000*100:+.2f}%")

    print(f"\nFILES:")
    print(f"  • memory/trades_history.json")
    print(f"  • memory/claude_calibration.json")
    print(f"  • reports/e2e_demo_report.txt")

    await connector.cleanup()

    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    print("\n[*] Starting 10-round trading session...")
    print("[*] Mode: PAPER (simulation only)\n")

    try:
        asyncio.run(run_trading_session())
    except KeyboardInterrupt:
        print("\n\n[X] Session interrupted")
    except Exception as e:
        print(f"\n\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
