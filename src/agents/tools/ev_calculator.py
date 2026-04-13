"""
Expected Value Calculator - Determine if market is mispriced
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EVCalculator:
    """
    Calculate Expected Value when market price differs from estimated probability.

    Formula:
    EV = (Your_Probability * Payout) - (Market_Price * 1) - Fees
    Edge = (Your_Prob - Market_Price) / Market_Price

    Example:
        calc = EVCalculator()
        result = calc.calculate(
            market_price=0.38,  # Market says 38% for YES
            model_probability=0.42,  # You think 42%
        )
        # Returns: {
        #   "edge_percent": 4.2,
        #   "decision": "BUY",
        #   "expected_value": 0.04,
        #   "confidence": 0.75
        # }
    """

    def __init__(self, trading_fee: float = 0.001, execution_fee: float = 0.0005):
        """
        Initialize calculator

        Args:
            trading_fee: Fee for buying/selling (0.1% typical on Polymarket)
            execution_fee: Gas fee on Polygon (~0.05%)
        """
        self.trading_fee = trading_fee
        self.execution_fee = execution_fee
        self.total_fee = trading_fee + execution_fee

        logger.info(
            f"EVCalculator initialized (total fees: {self.total_fee:.02%})"
        )

    def calculate(
        self,
        market_price: float,
        model_probability: float,
        kelly_fraction: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Calculate expected value and trading decision

        Args:
            market_price: Current market price (0-1)
            model_probability: Your estimated probability (0-1)
            kelly_fraction: Kelly Criterion fraction (0.5 = half-Kelly, safer)

        Returns:
            {
                "edge_percent": float,  # Edge as percentage
                "decision": "BUY" | "SELL" | "PASS",
                "expected_value": float,  # EV per $1 bet
                "kelly_fraction": float,  # Recommended position size
                "confidence": float,  # 0-1
                "reasoning": str
            }
        """

        # Input validation
        if not (0 <= market_price <= 1) or not (0 <= model_probability <= 1):
            return {
                "edge_percent": 0,
                "decision": "PASS",
                "expected_value": 0,
                "kelly_fraction": 0,
                "confidence": 0,
                "reasoning": "Invalid input: prices must be 0-1",
            }

        # Edge calculation
        edge = model_probability - market_price
        edge_percent = edge * 100

        # Decision logic
        min_edge = 0.01  # Minimum 1% edge to trade
        min_kelly_fraction = 0.0025  # Minimum 0.25% position

        if abs(edge) < min_edge:
            return {
                "edge_percent": edge_percent,
                "decision": "PASS",
                "expected_value": edge - self.total_fee,
                "kelly_fraction": 0,
                "confidence": 0.50,
                "reasoning": f"Edge too small: {edge_percent:.2f}% (min: {min_edge*100:.1f}%)",
            }

        # Determine direction
        if edge > 0:
            decision = "BUY"
            # YOU think probability is HIGHER than market price
            # So you buy YES at discounted market_price
        else:
            decision = "SELL"
            # YOU think probability is LOWER than market price
            # So you sell YES at inflated market_price

        # Kelly Criterion position sizing
        # Kelly % = (BP - Q) / B
        # B = odds, P = win prob, Q = lose prob
        edge_kelly = edge / (1 - market_price) if market_price < 1 else 0

        # Apply Kelly fraction (conservative)
        kelly_position = max(min_kelly_fraction, kelly_fraction * edge_kelly)
        kelly_position = min(0.25, kelly_position)  # Max 25% per trade

        # Expected value (accounting for fees)
        if decision == "BUY":
            # Win: market_price becomes 1.0, gain = (1 - market_price - fee)
            # Lose: market_price becomes 0, loss = market_price + fee
            ev_per_dollar = (
                model_probability * (1 - market_price - self.total_fee)
                - (1 - model_probability) * (market_price + self.total_fee)
            )
        else:
            # Selling YES (betting on NO)
            ev_per_dollar = (
                (1 - model_probability)
                * (market_price - self.total_fee)
                - model_probability * (1 - market_price + self.total_fee)
            )

        # Confidence: higher edge = higher confidence
        confidence = min(0.95, max(0.55, 0.50 + (abs(edge) * 5)))

        reasoning = (
            f"Edge: {edge_percent:.1f}% | "
            f"Market: {market_price:.1%} vs Model: {model_probability:.1%} | "
            f"EV per $1: ${ev_per_dollar:.4f} | "
            f"Kelly position: {kelly_position:.2%}"
        )

        return {
            "edge_percent": edge_percent,
            "decision": decision,
            "expected_value": ev_per_dollar,
            "kelly_fraction": kelly_position,
            "confidence": confidence,
            "reasoning": reasoning,
        }


# Singleton instance
_calculator = EVCalculator()


def expected_value_calculator(
    market_price: float,
    model_probability: float,
    kelly_fraction: float = 0.5,
) -> Dict[str, Any]:
    """
    Tool function for Claude to call

    Args:
        market_price: Current market price (0-1)
        model_probability: Claude's estimated probability (0-1)
        kelly_fraction: Kelly Criterion fraction (default 0.5 = half-Kelly, safer)

    Returns:
        EV calculation with decision recommendation
    """
    return _calculator.calculate(market_price, model_probability, kelly_fraction)
