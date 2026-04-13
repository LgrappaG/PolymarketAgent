"""
Polymarket AI Agent - Main Entry Point

Architecture:
  1. Data Collectors: Parallel data gathering (polls, sports, crypto, news)
  2. Claude Decision Engine: Tool-use based analysis & decision making
  3. Semi-autonomous Executor: Risk-managed trade execution
  4. Memory System: Trade history & performance tracking
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

from src.config import get_settings, MONITORED_MARKETS
from src.data.datastore import DataStore
from src.agents.claude_agent import ClaudeAgent
from src.execution.executor import TradeExecutor
from src.memory.performance_tracker import PerformanceTracker

# Configure logging
logger = logging.getLogger(__name__)


class PolymarketAgent:
    """Main orchestrator for Polymarket AI Agent"""

    def __init__(self):
        """Initialize agent components"""
        self.settings = get_settings()
        self.datastore = DataStore()
        self.claude_agent = ClaudeAgent()
        self.executor = TradeExecutor()
        self.performance = PerformanceTracker()

        logger.info(f"PolymarketAgent initialized (v0.1.0)")
        logger.info(f"Execution mode: {self.settings.execution_mode}")
        logger.info(f"Initial balance: ${self.settings.initial_balance} USDC")

    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing agent components...")
        await self.datastore.initialize()
        await self.executor.connect()
        logger.info("✓ Initialization complete")

    async def run_once(self):
        """Single iteration of the agent loop"""
        logger.info(f"=== Agent Iteration @ {datetime.now().isoformat()} ===")

        try:
            # 1. Collect data
            logger.info("📊 Collecting market data...")
            markets_data = await self.datastore.get_latest_data()

            if not markets_data:
                logger.warning("No market data available")
                return

            # 2. Claude decision making
            logger.info("🧠 Claude analyzing opportunities...")
            decisions = await self.claude_agent.analyze_markets(markets_data)

            if not decisions:
                logger.info("No trading opportunities found")
                return

            # 3. Execute trades
            logger.info("💱 Processing trade decisions...")
            for decision in decisions:
                logger.info(f"  Decision: {decision}")

                result = await self.executor.process_decision(
                    decision, mode=self.settings.execution_mode
                )

                if result:
                    self.performance.log_trade(decision, result)

            logger.info("✓ Iteration complete\n")

        except Exception as e:
            logger.error(f"Error in agent loop: {e}", exc_info=True)

    async def run_continuous(self, poll_interval: int = 300):
        """Continuous agent loop"""
        logger.info(f"Starting continuous mode (polling every {poll_interval}s)")

        try:
            while True:
                await self.run_once()
                await asyncio.sleep(poll_interval)
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("Shutting down agent...")
        await self.executor.disconnect()
        self.performance.save()
        logger.info("✓ Shutdown complete")

    def print_status(self):
        """Print current agent status"""
        status = {
            "Balance": f"${self.settings.initial_balance}",
            "Execution Mode": self.settings.execution_mode,
            "Monitored Markets": len(MONITORED_MARKETS),
            "Trading Confidence Threshold": f"{self.settings.min_confidence_auto:.0%}",
            "Max Position Size": f"{self.settings.max_position_size:.1%}",
        }

        print("\n" + "=" * 50)
        print("POLYMARKET AI AGENT - STATUS")
        print("=" * 50)
        for key, value in status.items():
            print(f"  {key:<30} {value}")
        print("=" * 50 + "\n")


async def main():
    """Main entry point"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/agent.log"),
        ],
    )

    logger.info("=" * 60)
    logger.info("POLYMARKET AI AGENT - STARTING")
    logger.info("=" * 60)

    # Initialize agent
    agent = PolymarketAgent()
    agent.print_status()

    try:
        await agent.initialize()

        # Run in continuous mode
        await agent.run_continuous(poll_interval=300)  # 5 minutes

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
