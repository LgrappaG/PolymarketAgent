"""Debug live execution with detailed logging"""

import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datastore import DataStore
from src.agents.claude_agent import ClaudeAgent
from src.execution.executor import TradeExecutor
from src.execution.polymarket_connector import PolymarketConnector
from src.execution.risk_manager import RiskManager, RiskConfig
from src.memory.performance_tracker import PerformanceTracker
from src.config import get_settings

# Enable DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s'
)

logger = logging.getLogger(__name__)


async def debug_live_execution():
    """Run live execution with debug logging"""

    print("\n" + "="*100)
    print("DEBUG: LIVE EXECUTION TEST")
    print("="*100 + "\n")

    settings = get_settings()

    # Initialize
    logger.info("[START] Initializing components...")
    datastore = DataStore(newsapi_key=settings.news_api_key)
    await datastore.initialize()

    agent = ClaudeAgent()
    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    risk_config = RiskConfig(initial_balance=10000)
    tracker = PerformanceTracker()
    executor = TradeExecutor(connector, risk_config, tracker)

    logger.info("[START] Components initialized")

    # Get market data
    logger.info("[STEP 1] Fetching market data...")
    market_data = await datastore.get_latest_data()
    logger.info(f"[STEP 1] Got market data: {len(market_data.get('markets', []))} markets, "
                f"{len(market_data.get('polls', []))} polls, "
                f"{len(market_data.get('sports', []))} sports")

    # Get Claude decisions
    logger.info("[STEP 2] Generating Claude decisions...")
    decisions = await agent.analyze_markets(market_data)
    logger.info(f"[STEP 2] Generated {len(decisions)} decisions")

    if not decisions:
        logger.error("[STEP 2] ERROR: No decisions generated!")
        await connector.cleanup()
        return

    for idx, d in enumerate(decisions):
        logger.info(f"[STEP 2] Decision {idx+1}: market='{d.get('market')}', "
                    f"confidence={d.get('confidence'):.0%}, "
                    f"decision={d.get('decision')}")

    # Execute decisions
    logger.info("[STEP 3] Executing decisions in LIVE mode...")
    report = await executor.execute_decisions(
        decisions=decisions,
        market_data=market_data,
        execution_mode="LIVE"
    )

    logger.info(f"[STEP 3] Execution complete")
    logger.info(f"[STEP 3] Report: {report['executed']} executed, {report['rejected']} rejected")

    # Print detailed report
    print("\n" + "="*100)
    print("EXECUTION REPORT")
    print("="*100)
    print(f"Total Decisions: {report['total_decisions']}")
    print(f"Executed: {report['executed']}")
    print(f"Rejected: {report['rejected']}")
    print(f"Balance: ${report['balance']:.2f}")
    print(f"Drawdown: {report['drawdown']:.1%}")

    if report['executions']:
        print(f"\n[+] EXECUTED ORDERS:")
        for exec_order in report['executions']:
            print(f"    {exec_order['order_id']:20s} | {exec_order['market'][:30]:30s} | "
                  f"{exec_order['decision']:4s} x{exec_order['position_size']:.0f} @ ${exec_order['entry_price']:.3f}")
    else:
        print(f"\n[X] No orders executed")

    if report['rejected_trades']:
        print(f"\n[!] REJECTED TRADES:")
        for rej in report['rejected_trades']:
            print(f"    {rej['market'][:50]:50s} | Reason: {rej['reason']}")

    print("\n" + "="*100 + "\n")

    await connector.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(debug_live_execution())
    except KeyboardInterrupt:
        print("\n\n[X] Interrupted")
    except Exception as e:
        logger.error(f"[ERROR] {e}", exc_info=True)
        print(f"\n\n[X] Error: {e}")
