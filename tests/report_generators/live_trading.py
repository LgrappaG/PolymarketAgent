"""
LIVE TRADING MODE - Real Polymarket execution
With conservative risk limits and monitoring
"""

import asyncio
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datastore import DataStore
from src.agents.claude_agent import ClaudeAgent
from src.execution.executor import TradeExecutor
from src.execution.polymarket_connector import PolymarketConnector
from src.execution.risk_manager import RiskManager, RiskConfig
from src.memory.performance_tracker import PerformanceTracker
from src.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_live_trading():
    """Run complete live trading cycle"""

    print("\n" + "=" * 100)
    print("POLYMARKET AGENT - LIVE TRADING MODE")
    print("=" * 100)
    print(f"Start Time: {datetime.now().isoformat()}\n")

    logger.info("LIVE TRADING SESSION STARTED")

    # Load settings
    settings = get_settings()
    logger.info(f"Config loaded: {settings.execution_mode} mode")

    # ========== PHASE 1: DATA COLLECTION ==========
    print("[1] DATA COLLECTION (Real Markets)")
    print("-" * 100)

    datastore = DataStore(newsapi_key=settings.news_api_key)
    await datastore.initialize()

    print("Fetching live market data...")
    market_data = await datastore.get_latest_data()

    print(f"[+] Data collected: {len(market_data)} sources")
    for source in market_data.keys():
        print(f"    • {source}")

    # ========== PHASE 2: CLAUDE ANALYSIS ==========
    print("\n[2] CLAUDE ANALYSIS (Market Decision Engine)")
    print("-" * 100)

    agent = ClaudeAgent()
    print("Analyzing markets with tool-use...")

    decisions = await agent.analyze_markets(market_data)

    if decisions:
        print(f"[+] {len(decisions)} trading decision(s) generated:\n")
        for i, d in enumerate(decisions, 1):
            print(f"  {i}. Market: {d.get('market', 'Unknown')[:50]}")
            print(f"     Decision: {d.get('decision')} @ {d.get('confidence', 0):.0%} confidence")
            if "edge_percent" in d:
                print(f"     Edge: {d.get('edge_percent', 0):.2f}%")
            print()

            # Log prediction for calibration
            perf_tracker = PerformanceTracker()
            perf_tracker.log_prediction(
                market=d.get('market', 'Unknown'),
                claude_confidence=d.get('confidence', 0.5),
                predicted_direction=d.get('decision', 'PASS'),
                actual_outcome='PENDING'
            )
    else:
        print("[!] No decisions generated")
        print("Exiting without execution")
        return

    # ========== PHASE 3: INITIALIZE EXECUTOR ==========
    print("\n[3] EXECUTOR INITIALIZATION")
    print("-" * 100)

    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    risk_config = RiskConfig(
        initial_balance=settings.initial_balance,
        max_position_size=0.01,  # 1% per trade (conservative)
        max_portfolio_draw_down=0.10,  # 10% max drawdown
        min_confidence=0.70,
    )

    tracker = PerformanceTracker()
    executor = TradeExecutor(
        polymarket_connector=connector,
        risk_config=risk_config,
        performance_tracker=tracker,
    )

    print(f"[+] Executor ready")
    print(f"    Balance: ${risk_config.initial_balance:.2f}")
    print(f"    Max position: {risk_config.max_position_size:.1%}")
    print(f"    Min confidence: {risk_config.min_confidence:.0%}")
    print(f"    Max drawdown: {risk_config.max_portfolio_draw_down:.1%}")

    # ========== PHASE 4: LIVE EXECUTION ==========
    print("\n[4] LIVE EXECUTION")
    print("-" * 100)

    print(f"Executing {len(decisions)} decisions in LIVE mode...\n")

    execution_report = await executor.execute_decisions(
        decisions=decisions,
        market_data=market_data,
        execution_mode="LIVE"
    )

    print(f"\n[EXECUTION SUMMARY]")
    print(f"  Total decisions: {execution_report['total_decisions']}")
    print(f"  Executed: {execution_report['executed']}")
    print(f"  Rejected: {execution_report['rejected']}")
    print(f"  Balance: ${execution_report['balance']:.2f}")
    print(f"  Drawdown: {execution_report['drawdown']:.1%}")

    if execution_report['executions']:
        print(f"\n[LIVE ORDERS PLACED]")
        for exec_order in execution_report['executions']:
            print(f"\n  Order ID: {exec_order.get('order_id', 'N/A')}")
            print(f"  Market: {exec_order['market']}")
            print(f"  Decision: {exec_order['decision']}")
            print(f"  Position: {exec_order['position_size']:.0f} shares")
            print(f"  Entry Price: ${exec_order['entry_price']:.3f}")
            print(f"  Status: {exec_order['status']}")
            print(f"  Confidence: {exec_order['confidence']:.0%}")

    if execution_report['rejected_trades']:
        print(f"\n[REJECTED TRADES]")
        for reject in execution_report['rejected_trades']:
            print(f"  {reject['market']}: {reject['reason']}")

    # ========== PHASE 5: MONITORING ==========
    print("\n[5] LIVE MONITORING")
    print("-" * 100)

    print("\n[*] Open positions:")
    open_trades = tracker.get_open_trades()

    if open_trades:
        for trade in open_trades:
            print(f"\n  Trade #{trade['id']}: {trade['market']}")
            print(f"  Entry: ${trade['entry_price']:.3f} x {trade['position_size']:.0f}")
            print(f"  Confidence: {trade['confidence']:.0%}")
            print(f"  Status: {trade['status']}")
            print(f"  Timestamp: {trade['timestamp']}")
    else:
        print("  No open positions")

    # ========== REPORTS ==========
    print("\n[6] PERFORMANCE REPORTS")
    print("-" * 100)

    tracker.print_summary()

    # Export
    tracker.export_full_report("reports/live_trading_session.txt")
    print(f"\n[+] Full report exported to: reports/live_trading_session.txt")
    print(f"[+] Trade history: memory/trades_history.json")
    print(f"[+] Calibration: memory/claude_calibration.json")

    # ========== FINAL STATUS ==========
    print("\n" + "=" * 100)
    print("LIVE TRADING SESSION SUMMARY")
    print("=" * 100)
    print(f"""
Status: ACTIVE
Mode: LIVE
Start Time: {datetime.now().isoformat()}

Decisions: {len(decisions)} generated
Executed: {execution_report['executed']} orders placed
Rejected: {execution_report['rejected']} orders

Account Balance: ${execution_report['balance']:.2f}
Current Drawdown: {execution_report['drawdown']:.1%}

Next Steps:
  1. Monitor open positions in memory/trades_history.json
  2. Check Polymarket account for order status
  3. Set stop-loss and take-profit alerts
  4. Review performance in reports/

RISK ACTIVE: Real funds deployed!
""")
    print("=" * 100 + "\n")

    await connector.cleanup()
    logger.info("LIVE TRADING SESSION ENDED")


if __name__ == "__main__":
    print("\n[!] WARNING: LIVE TRADING MODE ACTIVATED")
    print("[!] Real funds will be deployed on Polymarket")
    print("[!] Ensure sufficient balance in wallet")
    print("\nContinue? (Type 'YES' to proceed):")

    confirm = input().strip().upper()

    if confirm != "YES":
        print("[X] Cancelled - exiting")
        sys.exit(0)

    print("\n[*] Starting live trading...\n")

    try:
        asyncio.run(run_live_trading())
    except KeyboardInterrupt:
        print("\n\n[X] Trading interrupted by user")
        logger.info("Trading interrupted by user")
    except Exception as e:
        print(f"\n\n[X] Error: {e}")
        logger.error(f"Critical error: {e}", exc_info=True)
