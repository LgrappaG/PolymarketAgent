"""Semi-autonomous Trade Executor - Execute decisions from Claude"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.execution.polymarket_connector import PolymarketConnector
from src.execution.risk_manager import RiskManager, RiskConfig
from src.memory.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Execute trading decisions from Claude Agent"""

    def __init__(
        self,
        polymarket_connector: PolymarketConnector,
        risk_config: RiskConfig = None,
        performance_tracker: PerformanceTracker = None,
    ):
        self.connector = polymarket_connector
        self.risk_manager = RiskManager(risk_config or RiskConfig())
        self.performance_tracker = performance_tracker or PerformanceTracker()

        self.active_positions: Dict[str, Dict] = {}
        self.execution_log: List[Dict] = []

        logger.info("TradeExecutor initialized")

    async def execute_decisions(
        self,
        decisions: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        execution_mode: str = "PAPER",  # PAPER or LIVE
    ) -> Dict[str, Any]:
        """
        Execute trading decisions from Claude

        Args:
            decisions: List of trading decisions
            market_data: Current market data
            execution_mode: PAPER (simulation) or LIVE (real trading)

        Returns:
            Execution report
        """

        logger.info(
            f"Executing {len(decisions)} decisions (mode={execution_mode})..."
        )

        executions = []
        rejected = []

        for idx, decision in enumerate(decisions):
            market = decision.get("market", "Unknown")
            confidence = decision.get("confidence", 0.5)

            logger.debug(f"[Decision {idx+1}] Market: {market}, Confidence: {confidence:.0%}")

            # Risk check
            can_trade, reason = self.risk_manager.can_trade(confidence)

            if not can_trade:
                logger.warning(f"[Decision {idx+1}] Trade rejected: {market} - {reason}")
                rejected.append({"market": market, "reason": reason})
                continue

            logger.debug(f"[Decision {idx+1}] Risk check passed")

            # Calculate position
            entry_price = decision.get("entry_price", 0.50)
            position_size = self.risk_manager.calculate_position_size(
                confidence, entry_price
            )

            logger.debug(f"[Decision {idx+1}] Position size: {position_size:.2f} @ ${entry_price:.3f}")

            # Execute
            if execution_mode == "PAPER":
                logger.debug(f"[Decision {idx+1}] Executing PAPER trade")
                result = await self._execute_paper(decision, position_size)
            else:
                logger.debug(f"[Decision {idx+1}] Executing LIVE trade")
                result = await self._execute_live(decision, position_size)

            if result:
                logger.info(f"[Decision {idx+1}] Execution successful: {result.get('order_id')}")
                executions.append(result)
                self.execution_log.append(result)

                # Log to memory
                if self.performance_tracker:
                    self.performance_tracker.log_trade(
                        market=market,
                        decision=decision.get("decision", "PASS"),
                        confidence=confidence,
                        position_size=position_size,
                        entry_price=entry_price,
                        notes=f"Edge: {decision.get('edge_percent', 0):.1f}% | {execution_mode}",
                    )
            else:
                logger.error(f"[Decision {idx+1}] Execution returned None for {market}")

        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": execution_mode,
            "total_decisions": len(decisions),
            "executed": len(executions),
            "rejected": len(rejected),
            "executions": executions,
            "rejected_trades": rejected,
            "balance": self.risk_manager.current_balance,
            "drawdown": self.risk_manager.get_current_drawdown(),
        }

        logger.info(
            f"Execution complete: {len(executions)} executed, "
            f"{len(rejected)} rejected"
        )

        return report

    async def _execute_paper(
        self, decision: Dict[str, Any], position_size: float
    ) -> Optional[Dict]:
        """Paper trading (simulation)"""

        execution = {
            "type": "PAPER",
            "timestamp": datetime.now().isoformat(),
            "market": decision.get("market", "Unknown"),
            "decision": decision.get("decision", "PASS"),
            "confidence": decision.get("confidence", 0.5),
            "position_size": position_size,
            "entry_price": decision.get("entry_price", 0.50),
            "status": "SIMULATED",
            "order_id": f"PAPER_{len(self.execution_log):04d}",
        }

        logger.info(
            f"[PAPER] {execution['market'][:30]:<30} "
            f"{execution['decision']:>4} x{position_size:.0f} @ {execution['entry_price']:.3f}"
        )

        return execution

    async def _execute_live(
        self, decision: Dict[str, Any], position_size: float
    ) -> Optional[Dict]:
        """Live trading on Polymarket"""

        market = decision.get("market", "Unknown")
        side = decision.get("decision", "PASS")
        price = decision.get("entry_price", 0.50)

        logger.debug(f"[LIVE] Starting live execution: {market} {side} x{position_size} @ ${price:.3f}")

        try:
            # Get market ID from market name
            logger.debug(f"[LIVE] Fetching markets with search term: '{market}'")
            markets_response = await self.connector.get_markets(search=market)

            logger.debug(f"[LIVE] Markets response type: {type(markets_response)}")
            if isinstance(markets_response, dict):
                logger.debug(f"[LIVE] Response is dict with keys: {markets_response.keys()}")

            # Handle dict response (new API format) or list (fallback)
            if isinstance(markets_response, dict):
                markets = markets_response.get("data", [])
                logger.debug(f"[LIVE] Extracted 'data' from dict response: {len(markets)} markets")
            else:
                markets = markets_response or []
                logger.debug(f"[LIVE] Using list response directly: {len(markets)} markets")

            if not markets or len(markets) == 0:
                logger.warning(f"[LIVE] Market not found: {market}")
                return None

            logger.debug(f"[LIVE] Searching for market with valid ID among {len(markets)} markets")

            # Find first ACTIVE market with valid question_id (Polymarket uses question_id, not id)
            market_id = None
            market_question = None
            for idx, m in enumerate(markets):
                if isinstance(m, dict):
                    # Polymarket API uses question_id as the market identifier
                    q_id = m.get("question_id")
                    question = m.get("question", "Unknown")
                    is_active = m.get("accepting_orders", False) or not m.get("closed", True)

                    logger.debug(f"[LIVE]   Market[{idx}]: question='{question[:50]}...', "
                                f"question_id={q_id}, accepting_orders={m.get('accepting_orders')}, closed={m.get('closed')}")

                    if q_id:
                        market_id = q_id
                        market_question = question
                        logger.debug(f"[LIVE] Selected market ID: {market_id}, question: {market_question}")
                        break
                else:
                    logger.debug(f"[LIVE]   Market[{idx}]: Not a dict, type={type(m)}")

            if not market_id:
                logger.warning(f"[LIVE] No valid market ID found for: {market}")
                return None

            logger.info(f"[LIVE] Market ID resolved: {market_id}")

            # Place order
            logger.debug(f"[LIVE] Placing order: market_id={market_id}, side={side}, price={price}, size={position_size}")
            order = await self.connector.place_order(
                market_id=market_id,
                side=side,
                price=price,
                size=position_size,
                order_type="LIMIT",
            )

            logger.debug(f"[LIVE] Order response: {order}")

            if order:
                execution = {
                    "type": "LIVE",
                    "timestamp": datetime.now().isoformat(),
                    "market": market_question or market,
                    "market_id": market_id,
                    "decision": side,
                    "confidence": decision.get("confidence", 0.5),
                    "position_size": position_size,
                    "entry_price": price,
                    "order_id": order.get("id"),
                    "status": "PENDING",
                }

                logger.info(
                    f"[LIVE] Order placed: {market_question[:30] if market_question else market} {side} x{position_size}) "
                    f"@ {price:.3f} -> {order.get('id')}"
                )

                return execution
            else:
                logger.warning(f"[LIVE] Order returned None despite retry logic")

        except Exception as e:
            logger.error(f"[LIVE] Error executing live trade: {e}", exc_info=True)

        return None

    async def close_position(
        self, order_id: str, exit_price: float, reason: str = ""
    ) -> bool:
        """Close an open position"""

        try:
            await self.connector.cancel_order(order_id)

            # Update memory
            if self.performance_tracker:
                self.performance_tracker.close_trade(
                    trade_id=int(order_id.split("_")[-1])
                    if order_id.startswith("PAPER_")
                    else 1,
                    exit_price=exit_price,
                    notes=reason,
                )

            logger.info(f"Position closed: {order_id} @ {exit_price:.3f}")
            return True

        except Exception as e:
            logger.error(f"Error closing position: {e}")

        return False

    def get_status(self) -> Dict[str, Any]:
        """Get executor status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "risk_manager": self.risk_manager.get_status(),
            "active_positions": len(self.active_positions),
            "total_executions": len(self.execution_log),
            "last_execution": (
                self.execution_log[-1]["timestamp"]
                if self.execution_log
                else None
            ),
        }
