"""Data collectors for various market sources"""

from src.data.collectors.polls_collector import get_polls_collector
from src.data.collectors.sports_collector import get_sports_collector
from src.data.collectors.crypto_collector import get_crypto_collector
from src.data.collectors.news_collector import get_news_collector

__all__ = [
    "get_polls_collector",
    "get_sports_collector",
    "get_crypto_collector",
    "get_news_collector",
]
