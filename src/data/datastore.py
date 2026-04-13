"""Data collection and storage layer - Aggregates all data collectors"""

import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from src.data.collectors.polls_collector import get_polls_collector
from src.data.collectors.sports_collector import get_sports_collector
from src.data.collectors.crypto_collector import get_crypto_collector
from src.data.collectors.news_collector import get_news_collector

logger = logging.getLogger(__name__)


class DataStore:
    """Central data repository for market information"""

    def __init__(self, newsapi_key: str = "demo"):
        self.market_data = {}
        self.collectors = {
            "polls": get_polls_collector(),
            "sports": get_sports_collector(),
            "crypto": get_crypto_collector(),
            "news": get_news_collector(newsapi_key),
        }
        self.last_updated = None
        logger.info("DataStore initialized with 4 collectors")

    async def initialize(self):
        """Initialize data collectors (parallel)"""
        logger.info("DataStore: Initializing collectors...")
        # Collectors are initialized on-demand (lazy loading)
        logger.info("✓ Collectors ready (lazy-loaded)")

    async def get_latest_data(self) -> Dict[str, Any]:
        """Get latest market data from all collectors (parallel execution)"""
        logger.info("DataStore: Fetching latest market data (parallel)...")

        try:
            # Run all collectors in parallel
            tasks = {
                "politics": self.collectors["polls"].collect(),
                "sports": self.collectors["sports"].collect(),
                "crypto": self.collectors["crypto"].collect(),
                "news": self.collectors["news"].collect(),
            }

            results = await asyncio.gather(
                *tasks.values(), return_exceptions=True
            )

            # Combine results
            aggregated = {}
            for key, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Error collecting {key}: {result}")
                    aggregated[key] = {}
                else:
                    aggregated[key] = result

            self.market_data = aggregated
            self.last_updated = datetime.now().isoformat()

            logger.info(
                f"✓ Data collection complete ({len(aggregated)} categories)"
            )
            return aggregated

        except Exception as e:
            logger.error(f"Error in get_latest_data: {e}", exc_info=True)
            return {}

    def get_cached_data(self) -> Dict[str, Any]:
        """Get cached market data (doesn't fetch)"""
        return self.market_data

    def get_last_updated(self) -> Optional[str]:
        """Get timestamp of last data collection"""
        return self.last_updated

    async def refresh_category(self, category: str) -> Dict[str, Any]:
        """Refresh data for a specific category"""
        logger.info(f"DataStore: Refreshing {category}...")

        if category == "politics":
            data = await self.collectors["polls"].collect()
        elif category == "sports":
            data = await self.collectors["sports"].collect()
        elif category == "crypto":
            data = await self.collectors["crypto"].collect()
        elif category == "news":
            data = await self.collectors["news"].collect()
        else:
            logger.warning(f"Unknown category: {category}")
            return {}

        # Update market data
        self.market_data[category] = data
        self.last_updated = datetime.now().isoformat()

        logger.info(f"✓ {category} refreshed")
        return data
