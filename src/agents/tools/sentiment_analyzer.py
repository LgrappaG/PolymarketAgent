"""
Sentiment Analysis Tool - Analyze market sentiment from news/tweets
"""

import re
import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentScore(Enum):
    """Sentiment direction"""

    VERY_BULLISH = 0.90
    BULLISH = 0.70
    NEUTRAL = 0.50
    BEARISH = 0.30
    VERY_BEARISH = 0.10


class SentimentAnalyzer:
    """
    Analyze sentiment from text (news/tweets) about a market.
    Uses keyword matching + signal detection (MVP version).

    Example:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(
            market="Bitcoin above $50k",
            text="Fed cut rates 50bps. Bitcoin rallies +5%"
        )
        # Returns: {
        #   "sentiment": 0.75,
        #   "signals": ["rate_cut", "price_rally"],
        #   "confidence": 0.82
        # }
    """

    def __init__(self):
        self.bullish_keywords = {
            # Positive indicators
            "breakthrough": 0.85,
            "rally": 0.80,
            "surge": 0.80,
            "gains": 0.75,
            "approval": 0.80,
            "bullish": 0.85,
            "strong": 0.70,
            "momentum": 0.75,
            "bullrun": 0.85,
            "outperform": 0.75,
            "beat": 0.75,
            # Fed/macro positive
            "rate cut": 0.85,
            "dovish": 0.80,
            "quantitative easing": 0.80,
            "stimulus": 0.75,
            # Company/event positive
            "ipo success": 0.85,
            "earnings beat": 0.80,
            "partnership": 0.70,
            "acquisition": 0.65,
        }

        self.bearish_keywords = {
            # Negative indicators
            "crash": 0.85,
            "plunge": 0.85,
            "collapse": 0.85,
            "bearish": 0.85,
            "selloff": 0.80,
            "decline": 0.70,
            "weakness": 0.70,
            "concern": 0.60,
            "risk": 0.55,
            "underperform": 0.75,
            "miss": 0.75,
            # Fed/macro negative
            "rate hike": 0.85,
            "hawkish": 0.80,
            "inflation": 0.75,
            "recession": 0.85,
            # Company/event negative
            "bankruptcy": 0.90,
            "scandal": 0.85,
            "lawsuit": 0.75,
            "outage": 0.70,
        }

        logger.info("SentimentAnalyzer initialized")

    def analyze(
        self, market: str, text: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment for a specific market

        Args:
            market: Market name (e.g. "Bitcoin above $50k")
            text: News article or tweet text

        Returns:
            {
                "sentiment": 0.0-1.0,  # Probability of positive outcome
                "signals": List of detected signals,
                "confidence": 0.0-1.0,  # Confidence in the analysis
                "reasoning": str
            }
        """
        text_lower = text.lower()

        # Count keyword matches
        bullish_matches = 0
        bearish_matches = 0
        bullish_strength = 0
        bearish_strength = 0

        for keyword, strength in self.bullish_keywords.items():
            if keyword in text_lower:
                bullish_matches += 1
                bullish_strength += strength

        for keyword, strength in self.bearish_keywords.items():
            if keyword in text_lower:
                bearish_matches += 1
                bearish_strength += strength

        # Calculate net sentiment
        if bullish_matches + bearish_matches == 0:
            # No signals found
            return {
                "sentiment": 0.50,
                "signals": [],
                "confidence": 0.20,
                "reasoning": "No market-relevant signals detected",
            }

        # Normalize scores
        total_strength = bullish_strength + bearish_strength
        bullish_score = bullish_strength / total_strength if total_strength > 0 else 0
        bearish_score = bearish_strength / total_strength if total_strength > 0 else 0

        # Calculate confidence (more signals = higher confidence)
        total_signals = bullish_matches + bearish_matches
        confidence = min(0.95, 0.3 + (total_signals * 0.15))

        # Determine sentiment
        sentiment = (bullish_score * 0.7) + (0.50 * 0.3)  # Weighted blend
        sentiment = max(0.05, min(0.95, sentiment))  # Clamp to [0.05, 0.95]

        # Gather signals
        detected_signals = []
        if "rate cut" in text_lower or "dovish" in text_lower:
            detected_signals.append("fed_dovish")
        if "bankruptcy" in text_lower or "scandal" in text_lower:
            detected_signals.append("company_negative")
        if bullish_matches > bearish_matches:
            detected_signals.append("net_bullish")
        else:
            detected_signals.append("net_bearish")

        reasoning = (
            f"Bullish signals: {bullish_matches}, Bearish signals: {bearish_matches}. "
            f"Net score: {sentiment:.0%}"
        )

        return {
            "sentiment": sentiment,
            "signals": detected_signals,
            "confidence": confidence,
            "reasoning": reasoning,
        }


# Singleton instance
_analyzer = SentimentAnalyzer()


def sentiment_analyzer(market: str, text: str) -> Dict[str, Any]:
    """
    Tool function for Claude to call

    Args:
        market: Market name
        text: News/tweet text to analyze

    Returns:
        Analysis result with sentiment score
    """
    return _analyzer.analyze(market, text)
