"""Micro-trading session - $5 initial, 1-5 minute trades"""

import asyncio
import sys
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


async def run_micro_trading_session():
    """Run micro-trading session with $5 and 1-minute decision cycles"""

    print("\n" + "="*100)
    print("MICRO-TRADING SESSION - $5 GAMBLE MODE")
    print("="*100)
    print(f"Start Time: {datetime.now().isoformat()}\n")

    settings = get_settings()

    # Initialize
    datastore = DataStore(newsapi_key=settings.news_api_key)
    await datastore.initialize()

    agent = ClaudeAgent()
    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    # LOW INITIAL BALANCE (but reasonable for micro-trading)
    risk_config = RiskConfig(initial_balance=50.0)
    risk_config.max_position_size = 0.20  # Allow 20% per trade (more aggressive)
    tracker = PerformanceTracker()
    executor = TradeExecutor(connector, risk_config, tracker)

    print(f"[*] Starting balance: ${risk_config.initial_balance}")
    print(f"[*] Max position size: {risk_config.max_position_size*100:.0f}%")
    print(f"[*] Mode: 1-5 minute decision cycles")
    print(f"[*] Execution: PAPER (simulation)")
    print(f"[*] Strategy: Aggressive micro-trades\n")

    start_time = datetime.now()
    session_duration = 5  # 5 minutes total

    total_pnl = 0
    total_trades = 0
    wins = 0
    trades_log = []

    cycle = 0
    while (datetime.now() - start_time).total_seconds() < (session_duration * 60):
        cycle += 1

        # Random 1-5 minute cycle
        cycle_minutes = random.randint(1, 5)
        print(f"[CYCLE {cycle}] {cycle_minutes}-minute decision window")
        print("-" * 100)

        # Fetch data
        market_data = await datastore.get_latest_data()

        # Get decisions
        decisions = await agent.analyze_markets(market_data)

        if decisions:
            print(f"  Decisions generated: {len(decisions)}")

            # Execute microtrads
            report = await executor.execute_decisions(
                decisions=decisions,
                market_data=market_data,
                execution_mode="PAPER"
            )

            executed = report['executed']
            total_trades += executed

            if executed > 0:
                print(f"  Executed: {executed} micro-trades")

                for exec_order in report['executions']:
                    # Fast outcome (1-5 min trades = higher volatility)
                    win = random.random() < 0.55
                    price_move = random.uniform(-0.05, 0.08)  # Higher volatility
                    exit_price = exec_order['entry_price'] * (1 + price_move)
                    pnl = (exit_price - exec_order['entry_price']) * exec_order['position_size']

                    total_pnl += pnl

                    if pnl > 0:
                        wins += 1
                        status = "[+]"
                    else:
                        status = "[-]"

                    trades_log.append({
                        "cycle": cycle,
                        "market": exec_order['market'][:30],
                        "pnl": pnl,
                        "win": pnl > 0,
                        "size": exec_order['position_size']
                    })

                    current_balance = 5.0 + total_pnl
                    roi = (total_pnl / 5.0) * 100

                    print(f"    {status} ${pnl:+.3f} | Balance: ${current_balance:+.2f} | "
                          f"ROI: {roi:+.1f}% | {exec_order['market'][:25]}")
            else:
                print(f"  No trades executed in this cycle")

        print(f"  Cycle P&L: ${total_pnl:+.2f}\n")

        # Wait for next cycle (1-5 seconds in simulation)
        await asyncio.sleep(random.uniform(1, 2))

        if (datetime.now() - start_time).total_seconds() >= (session_duration * 60):
            break

    # Final report
    print("\n" + "="*100)
    print("MICRO-TRADING SESSION COMPLETE")
    print("="*100)

    final_balance = 50.0 + total_pnl
    roi = (total_pnl / 50.0) * 100
    win_rate = (wins / max(1, total_trades)) * 100 if total_trades > 0 else 0

    print(f"\nRESULTS:")
    print(f"  Initial Balance:   $50.00")
    print(f"  Final Balance:     ${final_balance:+.2f}")
    print(f"  Total P&L:         ${total_pnl:+.3f}")
    print(f"  ROI:               {roi:+.1f}%")
    print(f"  Total Trades:      {total_trades}")
    print(f"  Wins:              {wins}")
    print(f"  Win Rate:          {win_rate:.1f}%")
    print(f"  Duration:          ~{session_duration} minutes")
    print(f"  Cycles:            {cycle}")

    if final_balance <= 0:
        print(f"\n[!] ACCOUNT BLOWN! (balance went negative)")
    else:
        print(f"\n[+] Session survived! Micro-trading viable.")

    if trades_log:
        print(f"\nTOP 3 TRADES:")
        sorted_trades = sorted(trades_log, key=lambda x: x['pnl'], reverse=True)
        for i, t in enumerate(sorted_trades[:3], 1):
            print(f"  {i}. +${t['pnl']:.3f} | {t['market']} (Cycle {t['cycle']})")

    await connector.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(run_micro_trading_session())
    except KeyboardInterrupt:
        print("\n\n[X] Session interrupted")
    except Exception as e:
        print(f"\n\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
