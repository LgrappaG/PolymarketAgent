"""
Risk Calculator - Determine position size using Kelly Criterion
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RiskCalculator:
    """
    Calculate safe position size using Kelly Criterion and risk management rules.

    Kelly Formula: f* = (bp - q) / b
    where:
        f* = fraction of bankroll to bet
        b = odds (1 for binary markets like Polymarket)
        p = probability of winning
        q = 1 - p (probability of losing)

    For Polymarket (binary YES/NO):
        f* = p - (1 - p) = 2p - 1

    Example:
        calc = RiskCalculator(balance=1000)
        result = calc.calculate(
            confidence=0.75,
            edge_percent=4.2,
        )
        # Returns: {
        #   "position_size": 42.50,  # $42.50
        #   "kelly_percent": 2.1,  # 2.1% of balance
        #   "max_loss": 10.63,  # Max loss if wrong
        #   "risk_reward": 4.0,
        #   "recommendation": "SAFE"
        # }
    """

    def __init__(
        self,
        balance: float = 1000,
        max_position_percent: float = 0.05,
        max_loss_percent: float = 0.02,
        kelly_fraction: float = 0.5,
    ):
        """
        Initialize risk calculator

        Args:
            balance: Current account balance in USDC
            max_position_percent: Max position size as % of balance (safety)
            max_loss_percent: Max loss per trade as % of balance (stop-loss)
            kelly_fraction: Kelly Criterion fraction (0.5 = half-Kelly, conservative)
        """
        self.balance = balance
        self.max_position_percent = max_position_percent
        self.max_loss_percent = max_loss_percent
        self.kelly_fraction = kelly_fraction

        logger.info(
            f"RiskCalculator initialized: balance=${balance}, "
            f"max_position={max_position_percent:.1%}, "
            f"kelly_fraction={kelly_fraction}"
        )

    def calculate(
        self,
        confidence: float,
        edge_percent: float,
        market_price: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Calculate position size and risk metrics

        Args:
            confidence: 0-1, confidence level in the decision
            edge_percent: Percentage edge (e.g., 4.2 for 4.2%)
            market_price: Current market price (for loss calculation)

        Returns:
            {
                "position_size": float,  # Dollar amount to trade
                "kelly_percent": float,  # As % of balance
                "max_loss": float,  # Max loss if trade goes wrong
                "risk_reward": float,  # Ratio
                "recommendation": "SAFE" | "MEDIUM" | "AGGRESSIVE" | "TOO_RISKY",
                "reasoning": str
            }
        """

        # Input validation
        if confidence < 0.5:
            return {
                "position_size": 0,
                "kelly_percent": 0,
                "max_loss": 0,
                "risk_reward": 0,
                "recommendation": "TOO_RISKY",
                "reasoning": f"Confidence too low: {confidence:.0%}",
            }

        if edge_percent < 0.5:
            return {
                "position_size": 0,
                "kelly_percent": 0,
                "max_loss": 0,
                "risk_reward": 0,
                "recommendation": "TOO_RISKY",
                "reasoning": f"Edge too small: {edge_percent:.1f}%",
            }

        # Kelly Criterion calculation
        # For Polymarket: kelly_fraction = 2 * confidence - 1
        raw_kelly = (2 * confidence - 1) * (edge_percent / 100)

        # Apply Kelly fraction (half-Kelly is safer)
        kelly_size = raw_kelly * self.kelly_fraction

        # Convert to dollar amount, respecting limits
        kelly_dollars = self.balance * kelly_size
        kelly_as_percent = kelly_size * 100

        # Apply hard limits
        max_by_policy = self.balance * self.max_position_percent
        position_size = min(kelly_dollars, max_by_policy)

        # Calculate max loss (if trade goes to 0)
        max_loss = position_size * market_price

        # Risk/reward ratio
        potential_gain = position_size * (1 - market_price) if market_price < 1 else 0
        risk_reward = potential_gain / max_loss if max_loss > 0 else 0

        # Determine recommendation
        max_acceptable_loss = self.balance * self.max_loss_percent

        if max_loss > max_acceptable_loss:
            recommendation = "TOO_RISKY"
        elif kelly_size > 0.05:  # > 5% of balance
            recommendation = "AGGRESSIVE"
        elif kelly_size > 0.02:  # > 2% of balance
            recommendation = "MEDIUM"
        else:
            recommendation = "SAFE"

        reasoning = (
            f"Kelly: {kelly_as_percent:.2f}% | "
            f"Position: ${position_size:.2f} | "
            f"Max loss: ${max_loss:.2f} ({max_loss/self.balance*100:.2f}% of balance) | "
            f"Risk/Reward: {risk_reward:.1f}:1"
        )

        return {
            "position_size": position_size,
            "kelly_percent": kelly_as_percent,
            "max_loss": max_loss,
            "risk_reward": risk_reward,
            "recommendation": recommendation,
            "reasoning": reasoning,
        }


# Keep instance for module-level function
_calculator = None


def risk_calculator(
    balance: float,
    confidence: float,
    edge: float,
    market_price: float = 0.50,
) -> Dict[str, Any]:
    """
    Tool function for Claude to call

    Args:
        balance: Account balance in USDC
        confidence: Confidence level (0-1)
        edge: Edge percentage (e.g., 4.2 for 4.2%)
        market_price: Current market price (default 0.5)

    Returns:
        Position sizing recommendation with risk metrics
    """
    global _calculator
    if _calculator is None:
        _calculator = RiskCalculator(balance=balance)
    else:
        _calculator.balance = balance

    return _calculator.calculate(confidence, edge, market_price)
