"""
Configuration manager for Polymarket Agent
Loads and validates settings from .env.local
"""

from functools import lru_cache
from typing import Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application configuration"""

    # ========== ANTHROPIC ==========
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")

    # ========== BLOCKCHAIN ==========
    private_key: str = Field(..., alias="PRIVATE_KEY")
    polygon_rpc_url: str = Field(
        default="https://polygon-rpc.com", alias="POLYGON_RPC_URL"
    )
    wallet_address: str = Field(..., alias="WALLET_ADDRESS")

    # ========== POLYMARKET ==========
    polymarket_clob_url: str = Field(
        default="https://clob.polymarket.com", alias="POLYMARKET_CLOB_URL"
    )
    polymarket_api_key: str = Field(..., alias="POLYMARKET_API_KEY")
    polymarket_api_secret: str = Field(..., alias="POLYMARKET_API_SECRET")
    polymarket_api_passphrase: str = Field(..., alias="POLYMARKET_API_PASSPHRASE")

    # ========== DATA SOURCES ==========
    news_api_key: str = Field(..., alias="NEWS_API_KEY")
    twitter_bearer_token: str = Field(..., alias="TWITTER_BEARER_TOKEN")
    pinnacle_api_key: Optional[str] = Field(default=None, alias="PINNACLE_API_KEY")

    # ========== TRADING PARAMETERS ==========
    initial_balance: float = Field(default=500, alias="INITIAL_BALANCE")
    max_position_size: float = Field(default=0.02, alias="MAX_POSITION_SIZE")
    min_confidence_auto: float = Field(default=0.75, alias="MIN_CONFIDENCE_AUTO")
    min_confidence_approval: float = Field(
        default=0.60, alias="MIN_CONFIDENCE_APPROVAL"
    )
    max_loss_percent: float = Field(default=0.05, alias="MAX_LOSS_PERCENT")

    # ========== EXECUTION MODE ==========
    execution_mode: Literal["PAPER", "APPROVAL", "AUTO"] = Field(
        default="APPROVAL", alias="EXECUTION_MODE"
    )

    # ========== LOGGING ==========
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )
    log_file: str = Field(default="logs/agent.log", alias="LOG_FILE")

    # ========== DATA COLLECTION ==========
    poll_interval: int = Field(default=300, alias="POLL_INTERVAL")
    crypto_update_interval: int = Field(default=60, alias="CRYPTO_UPDATE_INTERVAL")

    # ========== ALERTS ==========
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")

    @field_validator("max_position_size")
    @classmethod
    def validate_position_size(cls, v):
        if not 0 < v < 1:
            raise ValueError("max_position_size must be between 0 and 1")
        return v

    @field_validator("min_confidence_auto")
    @classmethod
    def validate_confidence_auto(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("min_confidence_auto must be between 0 and 1")
        return v

    class Config:
        env_file = ".env.local"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Load settings from .env.local (cached)"""
    return Settings()


# ========== CONSTANTS ==========

# Market Categories
MARKET_CATEGORIES = {
    "POLITICS": "Siyaset",
    "SPORTS": "Spor",
    "CRYPTO": "Kripto",
    "SCIENCE_TECH": "Bilim/Tech",
    "GEOPOLITICAL": "Jeopolitik",
    "COMMODITIES": "Emtia",
}

# Confidence Levels for Decision Making
CONFIDENCE_LEVELS = {
    "VERY_HIGH": 0.85,  # Auto-trade
    "HIGH": 0.70,  # Approval queue
    "MEDIUM": 0.50,  # Human review
    "LOW": 0.30,  # Likely skip
}

# Risk Profiles
RISK_PROFILES = {
    "CONSERVATIVE": {
        "max_position_size": 0.01,  # 1%
        "min_confidence": 0.80,
        "kelly_fraction": 0.25,
    },
    "BALANCED": {
        "max_position_size": 0.02,  # 2%
        "min_confidence": 0.70,
        "kelly_fraction": 0.50,
    },
    "AGGRESSIVE": {
        "max_position_size": 0.05,  # 5%
        "min_confidence": 0.60,
        "kelly_fraction": 1.0,
    },
}

# Data Update Intervals (seconds)
UPDATE_INTERVALS = {
    "POLITICS": 300,  # 5 minutes
    "SPORTS": 600,  # 10 minutes
    "CRYPTO": 60,  # 1 minute (volatile)
    "NEWS": 120,  # 2 minutes
}

# Market Monitoring Targets (initial MVP)
MONITORED_MARKETS = {
    "POLITICS": [
        "Will Dem. nominee be different from Biden 2028?",
        "Rep. 2028 presidential nominee",
    ],
    "SPORTS": [
        "FIFA 2026 winner",
        "NBA 2025-26 champion",
    ],
    "CRYPTO": ["Bitcoin above $50k by April 2026"],
}

# Edge Thresholds (minimum edge required to trade)
MINIMUM_EDGE = {
    "POLITICS": 0.02,  # 2% required edge
    "SPORTS": 0.03,  # 3%
    "CRYPTO": 0.01,  # 1% (arbitrage)
    "ARBITRAGE": 0.005,  # 0.5% (cross-market)
}

# Category-specific update schedules
CATEGORY_SCHEDULE = {
    "POLITICS": {"interval": 300, "priority": "HIGH"},
    "SPORTS": {"interval": 600, "priority": "MEDIUM"},
    "CRYPTO": {"interval": 60, "priority": "VERY_HIGH"},
    "NEWS": {"interval": 120, "priority": "HIGH"},
}
