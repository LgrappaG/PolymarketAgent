"""
Arbitrage Detector - Find cross-market price inefficiencies
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ArbitrageDetector:
    """
    Detect arbitrage opportunities between Polymarket and traditional bookmakers.

    Example markets:
    - Polymarket: FIFA 2026 France YES = 0.18
    - Pinnacle: France 4.50 odds = 1/4.50 = 0.22 probability
    - Arbitrage: Buy Polymarket (0.18), Sell Pinnacle (0.22) = +4% spread

    MVP: Only compares two markets (Polymarket vs. one bookmaker)
    """

    def __init__(self, min_arbitrage_margin: float = 0.005):
        """
        Initialize arbitrage detector

        Args:
            min_arbitrage_margin: Minimum 0.5% margin required to trade
        """
        self.min_arbitrage_margin = min_arbitrage_margin
        logger.info(
            f"ArbitrageDetector initialized (min margin: {min_arbitrage_margin:.2%})"
        )

    def detect(
        self,
        polymarket_price: float,
        competitor_price: float,
        competitor_name: str = "Bookmaker",
    ) -> Dict[str, Any]:
        """
        Detect arbitrage between two markets

        Args:
            polymarket_price: Price on Polymarket (0-1)
            competitor_price: Price on competing market (0-1, or decimal odds)
            competitor_name: Name of competitor market

        Returns:
            {
                "arbitrage_exists": bool,
                "margin_percent": float,  # Profit margin %
                "action": Dict with trade instructions,
                "confidence": float,
                "reasoning": str
            }
        """

        # Validate inputs
        if not (0 <= polymarket_price <= 1):
            return {
                "arbitrage_exists": False,
                "margin_percent": 0,
                "action": None,
                "confidence": 0,
                "reasoning": f"Invalid Polymarket price: {polymarket_price}",
            }

        if not (0 < competitor_price):
            return {
                "arbitrage_exists": False,
                "margin_percent": 0,
                "action": None,
                "confidence": 0,
                "reasoning": f"Invalid competitor price: {competitor_price}",
            }

        # Handle decimal odds (e.g., 4.50 = 1/4.50 = 0.22)
        if competitor_price > 2:
            # Assume decimal odds
            competitor_probability = 1 / competitor_price
        else:
            competitor_probability = competitor_price

        # Triangle arbitrage (3-way)
        # For binary markets: NO price = 1 - YES price
        polymarket_no = 1 - polymarket_price
        competitor_no = 1 - competitor_probability

        # Check for opportunities
        arbitrages = []

        # Opportunity 1: Buy YES on Polymarket, Sell YES on Competitor
        margin1 = competitor_probability - polymarket_price
        if margin1 > self.min_arbitrage_margin:
            arbitrages.append(
                {
                    "type": "buy_poly_sell_competitor",
                    "margin": margin1,
                    "instruction": (
                        f"BUY YES on Polymarket @ ${polymarket_price:.3f}, "
                        f"SELL YES on {competitor_name} @ ${competitor_probability:.3f}"
                    ),
                }
            )

        # Opportunity 2: Buy YES on Competitor, Sell YES on Polymarket
        margin2 = polymarket_price - competitor_probability
        if margin2 > self.min_arbitrage_margin:
            arbitrages.append(
                {
                    "type": "buy_competitor_sell_poly",
                    "margin": margin2,
                    "instruction": (
                        f"BUY YES on {competitor_name} @ ${competitor_probability:.3f}, "
                        f"SELL YES on Polymarket @ ${polymarket_price:.3f}"
                    ),
                }
            )

        if not arbitrages:
            return {
                "arbitrage_exists": False,
                "margin_percent": 0,
                "action": None,
                "confidence": 0.90,
                "reasoning": (
                    f"No arbitrage detected. "
                    f"Polymarket: {polymarket_price:.1%}, "
                    f"{competitor_name}: {competitor_probability:.1%}, "
                    f"Spread: {abs(margin1):.1%}"
                ),
            }

        # Best arbitrage
        best_arb = max(arbitrages, key=lambda x: x["margin"])

        # Account for fees (0.15% total: 0.10% trading + 0.05% gas)
        fees = 0.0015
        net_margin = best_arb["margin"] - fees

        # Confidence based on margin size
        confidence = min(0.98, 0.70 + (best_arb["margin"] * 10))

        reasoning = (
            f"Arbitrage: {best_arb['margin']:.2%} spread. "
            f"After fees (0.15%): {net_margin:.2%} profit per $1. "
            f"Type: {best_arb['type']}"
        )

        action = {
            "market": "Unknown",  # Will be filled by agent
            "arbitrage_type": best_arb["type"],
            "instruction": best_arb["instruction"],
            "position_size": None,  # To be calculated by risk calculator
        }

        return {
            "arbitrage_exists": net_margin > 0,
            "margin_percent": net_margin * 100,
            "action": action if net_margin > 0 else None,
            "confidence": confidence,
            "reasoning": reasoning,
        }


# Singleton instance
_detector = ArbitrageDetector()


def arbitrage_detector(
    polymarket_price: float,
    competitor_price: float,
    competitor_name: str = "Bookmaker",
) -> Dict[str, Any]:
    """
    Tool function for Claude to call

    Args:
        polymarket_price: Price on Polymarket (0-1)
        competitor_price: Price on competitor (0-1 or decimal odds)
        competitor_name: Name of competitor market

    Returns:
        Arbitrage detection result with trade instructions
    """
    return _detector.detect(polymarket_price, competitor_price, competitor_name)
