"""
News Collector - Sentiment and news data
Fetches news from NewsAPI and Twitter/X API for sentiment analysis
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import aiohttp

logger = logging.getLogger(__name__)


class NewsCollector:
    """Collect news from NewsAPI and social media"""

    def __init__(self, newsapi_key: str = "demo"):
        self.newsapi_key = newsapi_key
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.twitter_url = "https://api.twitter.com/2/tweets/search/recent"

        # Keywords for different markets
        self.market_keywords = {
            "politics": ["2028 election", "democrat", "republican", "biden", "trump"],
            "crypto": ["bitcoin", "ethereum", "crypto", "SEC", "fed rates"],
            "sports": ["fifa 2026", "world cup", "france", "nba finals"],
            "tech": ["AI", "deepseek", "quantum", "breakthrough"],
        }

        self.cache = {}
        logger.info("NewsCollector initialized")

    async def collect(self) -> Dict[str, Any]:
        """
        Collect latest news

        Returns:
            {
                "politics": {
                    "articles": [...],
                    "sentiment": 0.55,
                    "trending": True,
                    "timestamp": ISO
                },
                ...
            }
        """

        logger.info("NewsCollector: Fetching news...")

        results = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Fetch news for each category
                for category, keywords in self.market_keywords.items():
                    category_news = await self._fetch_news_category(
                        session, category, keywords
                    )
                    if category_news:
                        results[category] = category_news

        except Exception as e:
            logger.error(f"NewsCollector error: {e}")

        return results

    async def _fetch_news_category(
        self,
        session: aiohttp.ClientSession,
        category: str,
        keywords: List[str],
    ) -> Dict:
        """Fetch news for a specific category"""

        try:
            # Build query
            query = " OR ".join([f'"{kw}"' for kw in keywords[:3]])  # Limit to 3

            params = {
                "q": query,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 20,
                "apiKey": self.newsapi_key,
            }

            async with session.get(
                self.newsapi_url, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    articles = data.get("articles", [])

                    # Calculate sentiment from headlines
                    sentiment = await self._calculate_sentiment(
                        [a.get("title", "") for a in articles[:5]]
                    )

                    logger.debug(
                        f"News fetched for {category}: {len(articles)} articles"
                    )

                    return {
                        "category": category,
                        "articles_count": len(articles),
                        "recent_headlines": [
                            {
                                "title": a.get("title"),
                                "source": a.get("source", {}).get("name"),
                                "published_at": a.get("publishedAt"),
                            }
                            for a in articles[:5]
                        ],
                        "sentiment_score": sentiment,
                        "trending": len(articles) > 10,
                        "timestamp": datetime.now().isoformat(),
                    }

        except Exception as e:
            logger.warning(f"Could not fetch {category} news: {e}")

        # Fallback data
        return {
            "category": category,
            "articles_count": 0,
            "sentiment_score": 0.5,
            "trending": False,
            "timestamp": datetime.now().isoformat(),
        }

    async def _calculate_sentiment(self, texts: List[str]) -> float:
        """
        Simple sentiment calculation from text
        (In production: use ML model or API)
        """

        positive_words = [
            "gain",
            "surge",
            "rally",
            "bullish",
            "beat",
            "strong",
            "growth",
            "approval",
        ]
        negative_words = [
            "loss",
            "crash",
            "plunge",
            "bearish",
            "miss",
            "weak",
            "decline",
            "scandal",
        ]

        positive_count = 0
        negative_count = 0

        for text in texts:
            text_lower = text.lower()
            positive_count += sum(1 for word in positive_words if word in text_lower)
            negative_count += sum(1 for word in negative_words if word in text_lower)

        total = positive_count + negative_count

        if total == 0:
            return 0.5

        sentiment = positive_count / total
        return max(0.1, min(0.9, sentiment))

    async def search_market_news(self, market: str) -> List[Dict]:
        """
        Search news for a specific market

        Args:
            market: Market name

        Returns:
            List of relevant articles
        """

        all_news = await self.collect()

        for category, data in all_news.items():
            if market.lower() in category.lower() or market.lower() in str(
                data
            ).lower():
                return data.get("recent_headlines", [])

        return []

    async def get_trending_topics(self) -> Dict[str, Any]:
        """Get currently trending topics across all categories"""

        all_news = await self.collect()

        trending = {}
        for category, data in all_news.items():
            if data.get("trending"):
                trending[category] = {
                    "articles": data.get("articles_count"),
                    "sentiment": data.get("sentiment_score"),
                }

        return {
            "trending_categories": trending,
            "timestamp": datetime.now().isoformat(),
        }


# Singleton
_collector = None


def get_news_collector(newsapi_key: str = "demo") -> NewsCollector:
    """Get or create news collector instance"""
    global _collector
    if _collector is None:
        _collector = NewsCollector(newsapi_key)
    else:
        _collector.newsapi_key = newsapi_key
    return _collector
