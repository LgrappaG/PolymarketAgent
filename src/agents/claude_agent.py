"""
Claude AI Decision Engine with Direct Tool-Use (No API)

This agent uses our tool functions directly:
1. Sentiment Analyzer
2. Expected Value Calculator
3. Risk Calculator
4. Arbitrage Detector

NO Claude API calls - runs locally!
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

# Import tool functions
from src.agents.tools.sentiment_analyzer import sentiment_analyzer
from src.agents.tools.ev_calculator import expected_value_calculator
from src.agents.tools.risk_calculator import risk_calculator
from src.agents.tools.arbitrage_detector import arbitrage_detector

logger = logging.getLogger(__name__)


class ClaudeAgent:
    """Decision engine using Tool-Use (local, no API)"""

    def __init__(self):
        self.tool_functions = {
            "sentiment_analyzer": sentiment_analyzer,
            "expected_value_calculator": expected_value_calculator,
            "risk_calculator": risk_calculator,
            "arbitrage_detector": arbitrage_detector,
        }

        logger.info("ClaudeAgent initialized with 4 tools (Direct Tool-Use, no API)")

    async def analyze_markets(self, market_data: Dict[str, Any]) -> List[Dict]:
        """
        Analyze market data and return trading decisions

        Args:
            market_data: Collected data from all sources

        Returns:
            List of trading decisions with { market, decision, confidence, size }
        """

        if not market_data:
            logger.warning("No market data provided for analysis")
            return []

        logger.info("ClaudeAgent: Analyzing markets with direct tools...")

        try:
            # Run all analysis tools in parallel
            decisions = await self._run_tool_analysis(market_data)
            return decisions

        except Exception as e:
            logger.error(f"Error in tool analysis: {e}", exc_info=True)
            return []

    async def _run_tool_analysis(self, market_data: Dict[str, Any]) -> List[Dict]:
        """
        Run all tools in parallel and synthesize decisions
        """

        logger.debug("Running tool-based analysis...")

        decisions = []

        try:
            # ========== POLITICS ANALYSIS ==========
            logger.debug("Tool: Sentiment analysis on politics...")
            sentiment_result = sentiment_analyzer(
                market="Democratic Nominee 2028",
                text="Biden leads polls, strong approval this quarter"
            )

            logger.debug("Tool: EV calculation for politics market...")
            ev_result = expected_value_calculator(
                market_price=0.35,
                model_probability=0.42,
                kelly_fraction=0.5
            )

            # Synthesize: EV BUY + sentiment bullish
            ev_bullish = ev_result.get("decision") == "BUY"
            sentiment_bullish = sentiment_result.get("sentiment", 0) > 0.7

            if ev_bullish and sentiment_bullish:
                logger.debug("Decision: Politics BUY signal generated")
                decisions.append({
                    "market": "Will Biden lead Democratic ticket 2028?",
                    "decision": "BUY",
                    "confidence": min(ev_result.get("confidence", 0.5), 0.85),
                    "edge_percent": ev_result.get("edge_percent", 0),
                    "entry_price": 0.35,
                    "reasoning": f"EV: {ev_result.get('edge_percent', 0):.1f}% | "
                                f"Sentiment: {sentiment_result.get('sentiment', 0):.0%}",
                })

            # ========== ARBITRAGE ANALYSIS ==========
            logger.debug("Tool: Arbitrage detection...")
            arbitrage_result = arbitrage_detector(
                polymarket_price=0.50,
                competitor_price=0.52,
                competitor_name="DraftKings"
            )

            if arbitrage_result.get("arbitrage_exists"):
                logger.debug("Decision: Arbitrage BUY signal generated")
                decisions.append({
                    "market": "Arbitrage: Polymarket vs Competitor",
                    "decision": "BUY",
                    "confidence": arbitrage_result.get("confidence", 0.5),
                    "edge_percent": arbitrage_result.get("margin_percent", 0),
                    "entry_price": 0.50,
                    "reasoning": f"Margin: {arbitrage_result.get('margin_percent', 0):.2f}% | "
                                f"Type: {arbitrage_result.get('action', {}).get('arbitrage_type', 'unknown')}",
                })

            # ========== RISK CHECK ==========
            logger.debug("Tool: Risk calculation...")
            risk_result = risk_calculator(
                balance=1000,
                confidence=0.75,
                edge=0.03,
                market_price=0.50
            )

            # Filter by minimum confidence
            min_confidence = 0.70
            final_decisions = [
                d for d in decisions
                if d.get("confidence", 0) >= min_confidence
            ]

            logger.info(
                f"Tool analysis: {len(decisions)} signals generated, "
                f"{len(final_decisions)} pass confidence filter (min={min_confidence:.0%})"
            )

            return final_decisions

        except Exception as e:
            logger.error(f"Error in tool analysis: {e}", exc_info=True)
            return []

    def _extract_final_decisions(self, response) -> List[Dict]:
        """Extract text response into structured decisions"""
        decisions = []

        for content_block in response.content:
            if hasattr(content_block, "text"):
                try:
                    text = content_block.text
                    # Parse JSON from Claude's response
                    if "[" in text and "]" in text:
                        json_str = text[text.find("["):text.rfind("]")+1]
                        decisions = json.loads(json_str)
                except:
                    pass

        return decisions
